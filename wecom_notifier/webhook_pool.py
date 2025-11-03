"""
Webhook池 - 管理多个webhook的负载均衡和发送
"""
import queue
import threading
import time
from typing import List, Optional

from .logger import get_logger
from .constants import MSG_TYPE_TEXT, MSG_TYPE_MARKDOWN_V2, MSG_TYPE_IMAGE
from .models import Message, SendResult
from .segmenter import MessageSegmenter
from .sender import Sender
from .webhook_resource import WebhookResource
from .exceptions import WeComError


class AllWebhooksUnavailableError(WeComError):
    """所有webhook都不可用"""
    pass


class WebhookPool:
    """
    Webhook池

    管理多个webhook的负载均衡发送：
    - 全局消息队列（保证顺序）
    - 单线程调度器（串行处理）
    - 智能webhook选择（最空闲优先）
    - 自动容错和恢复
    """

    def __init__(
            self,
            resources: List[WebhookResource],
            sender: Sender,
            segmenter: MessageSegmenter,
            content_moderator: Optional['ContentModerator'] = None
    ):
        """
        初始化Webhook池

        Args:
            resources: Webhook资源列表
            sender: HTTP发送器
            segmenter: 消息分段器
            content_moderator: 内容审核器（可选）
        """
        self.logger = get_logger()
        self.resources = resources
        self.sender = sender
        self.segmenter = segmenter
        self.content_moderator = content_moderator

        if not self.resources:
            raise ValueError("Webhook pool must have at least one resource")

        # 消息队列
        self.message_queue = queue.Queue()

        # 结果字典
        self.results = {}

        # 停止标志
        self._stop_flag = threading.Event()

        # 调度线程
        self.scheduler_thread = threading.Thread(target=self._schedule_messages, daemon=True)
        self.scheduler_thread.start()

        self.logger.info(f"WebhookPool initialized with {len(self.resources)} webhooks")

    def enqueue(self, message: Message) -> SendResult:
        """
        将消息加入队列

        Args:
            message: 消息对象

        Returns:
            SendResult: 发送结果对象
        """
        result = SendResult(message.id)
        self.results[message.id] = result
        self.message_queue.put(message)

        self.logger.debug(f"Message {message.id} enqueued to pool (type={message.msg_type})")
        return result

    def _schedule_messages(self):
        """调度线程 - 串行处理消息"""
        self.logger.info("WebhookPool scheduler thread started")

        while not self._stop_flag.is_set():
            try:
                # 从队列获取消息（超时1秒）
                message = self.message_queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                # 处理消息
                self._process_message(message)
            except Exception as e:
                self.logger.error(f"Error processing message {message.id}: {e}")
                self.logger.exception(e)
                result = self.results.get(message.id)
                if result:
                    result.mark_failed(f"Internal error: {e}")
            finally:
                self.message_queue.task_done()

    def _process_message(self, message: Message):
        """
        处理单条消息（分段 + 发送）

        Args:
            message: 消息对象
        """
        result = self.results.get(message.id)
        if not result:
            self.logger.error(f"Result not found for message {message.id}")
            return

        self.logger.info(f"Processing message {message.id} in pool (type={message.msg_type})")

        # 分段
        segments = self._get_segments(message)
        total_segments = len(segments)

        self.logger.debug(f"Message {message.id} split into {total_segments} segments")

        # 审核分段（如果启用）
        if self.content_moderator and self.content_moderator.enabled:
            moderated_segments = []
            for segment in segments:
                # 跳过图片类型的审核
                if message.msg_type == MSG_TYPE_IMAGE:
                    moderated_segments.append(segment)
                    continue

                # 审核文本内容（传入message_id和msg_type）
                moderated_content = self.content_moderator.moderate(
                    content=segment.content,
                    message_id=message.id,
                    msg_type=message.msg_type
                )

                if moderated_content is None:
                    # 被拒绝，发送敏感词提示
                    self.logger.warning(f"Message {message.id} blocked by content moderator in pool")
                    alert_msg = self.content_moderator.create_block_alert(segment.content, message.id)

                    # 选择一个webhook发送提示消息
                    webhook = self._select_best_webhook()
                    webhook.rate_limiter.acquire()
                    self.sender.send_text(webhook.url, alert_msg)

                    result.mark_failed("Content blocked by moderator")
                    return

                # 使用审核后的内容
                from .models import SegmentInfo
                moderated_segment = SegmentInfo(
                    content=moderated_content,
                    is_first=segment.is_first,
                    is_last=segment.is_last,
                    page_number=segment.page_number,
                    total_pages=segment.total_pages
                )
                moderated_segments.append(moderated_segment)

            segments = moderated_segments

        # 记录使用的webhooks
        used_webhooks = set()

        # 发送每个分段
        for i, segment in enumerate(segments):
            # 选择最佳webhook
            try:
                webhook = self._select_best_webhook()
            except AllWebhooksUnavailableError as e:
                self.logger.error(f"All webhooks unavailable for message {message.id}")
                result.mark_failed(str(e))
                return

            # 频率控制
            webhook.rate_limiter.acquire()

            # 发送
            success, error = self._send_segment(message, segment.content, i, webhook.url)

            if success:
                # 成功
                webhook.mark_success()
                used_webhooks.add(webhook.url)
                self.logger.debug(
                    f"Segment {i + 1}/{total_segments} sent via {webhook.url[:30]}... "
                    f"for message {message.id}"
                )
            else:
                # 失败
                webhook.mark_failure()
                self.logger.warning(
                    f"Segment {i + 1}/{total_segments} failed via {webhook.url[:30]}...: {error}"
                )

                # 重试：尝试其他webhook
                retry_success = self._retry_segment(message, segment.content, i, used_webhooks)

                if not retry_success:
                    # 所有webhook都失败了
                    self.logger.error(
                        f"Segment {i + 1}/{total_segments} failed on all webhooks for message {message.id}"
                    )
                    result.mark_failed(f"Segment {i + 1}/{total_segments} failed on all webhooks")
                    return

            # 分段间延迟
            if i < total_segments - 1:
                time.sleep(message.segment_interval / 1000.0)

        # 处理@all workaround
        if message.needs_mention_all_workaround():
            self.logger.debug(f"Sending @all workaround for message {message.id}")

            webhook = self._select_best_webhook()
            webhook.rate_limiter.acquire()

            success, error = self.sender.send_mention_all(webhook.url)

            if success:
                webhook.mark_success()
                used_webhooks.add(webhook.url)
            else:
                webhook.mark_failure()
                self.logger.error(f"@all workaround failed for message {message.id}: {error}")
                result.mark_failed(f"@all workaround failed: {error}")
                return

        # 所有分段发送成功
        self.logger.info(
            f"Message {message.id} sent successfully ({total_segments} segments, "
            f"{len(used_webhooks)} webhooks)"
        )

        # 更新结果
        result.used_webhooks = list(used_webhooks)
        result.segment_count = total_segments
        result.mark_success()

    def _retry_segment(
            self,
            message: Message,
            content: str,
            segment_index: int,
            exclude_webhooks: set
    ) -> bool:
        """
        重试发送分段（尝试其他可用的webhook）

        Args:
            message: 消息对象
            content: 分段内容
            segment_index: 分段索引
            exclude_webhooks: 已经失败的webhook URL集合

        Returns:
            bool: 是否成功
        """
        # 获取所有可用的webhook（排除已失败的）
        available = [
            w for w in self.resources
            if w.is_available() and w.url not in exclude_webhooks
        ]

        if not available:
            return False

        # 按优先级排序
        available.sort(key=lambda w: w.get_priority_score(), reverse=True)

        # 依次尝试
        for webhook in available:
            webhook.rate_limiter.acquire()
            success, error = self._send_segment(message, content, segment_index, webhook.url)

            if success:
                webhook.mark_success()
                exclude_webhooks.add(webhook.url)
                self.logger.info(f"Segment {segment_index} retry succeeded via {webhook.url[:30]}...")
                return True
            else:
                webhook.mark_failure()
                self.logger.warning(f"Segment {segment_index} retry failed via {webhook.url[:30]}...")

        return False

    def _get_segments(self, message: Message):
        """
        获取消息分段

        Args:
            message: 消息对象

        Returns:
            List[SegmentInfo]: 分段列表
        """
        if message.msg_type == MSG_TYPE_IMAGE:
            from .models import SegmentInfo
            return [SegmentInfo(message.content, is_first=True, is_last=True)]

        return self.segmenter.segment(message.content, message.msg_type)

    def _send_segment(
            self,
            message: Message,
            content: str,
            segment_index: int,
            webhook_url: str
    ) -> tuple:
        """
        发送单个分段

        Args:
            message: 消息对象
            content: 分段内容
            segment_index: 分段索引
            webhook_url: Webhook地址

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        if message.msg_type == MSG_TYPE_TEXT:
            return self.sender.send_text(
                webhook_url,
                content,
                mentioned_list=message.mentioned_list if segment_index == 0 else None,
                mentioned_mobile_list=message.mentioned_mobile_list if segment_index == 0 else None
            )

        elif message.msg_type == MSG_TYPE_MARKDOWN_V2:
            return self.sender.send_markdown(webhook_url, content)

        elif message.msg_type == MSG_TYPE_IMAGE:
            if isinstance(content, tuple) and len(content) == 2:
                base64_data, md5_value = content
                return self.sender.send_image(webhook_url, base64_data, md5_value)
            else:
                return False, f"Invalid image content format"

        else:
            return False, f"Unsupported message type: {message.msg_type}"

    def _select_best_webhook(self) -> WebhookResource:
        """
        选择最佳webhook（最空闲优先策略）

        Returns:
            WebhookResource: 最佳webhook

        Raises:
            AllWebhooksUnavailableError: 所有webhook都不可用
        """
        # 过滤可用的webhook
        available = [w for w in self.resources if w.is_available()]

        if not available:
            # 所有webhook都在冷却期
            # 等待最早恢复的那个
            min_cooldown = min(w.get_cooldown_remaining() for w in self.resources)

            if min_cooldown > 0:
                self.logger.warning(
                    f"All webhooks in cooldown, waiting {min_cooldown:.1f}s for recovery"
                )
                time.sleep(min_cooldown + 0.1)  # 额外加0.1秒确保恢复

                # 重新检查
                available = [w for w in self.resources if w.is_available()]

            if not available:
                raise AllWebhooksUnavailableError("All webhooks are unavailable after waiting")

        # 按优先级分数排序（配额多的优先）
        best = max(available, key=lambda w: w.get_priority_score())

        # 如果最好的也是0配额，需要等待
        if best.rate_limiter.get_available_count() == 0:
            # 计算所有可用webhook中最快恢复的
            next_times = [(w, w.rate_limiter.get_next_available_time()) for w in available]
            soonest = min(next_times, key=lambda x: x[1])
            wait_time = soonest[1] - time.time()

            if wait_time > 0:
                self.logger.debug(f"Waiting {wait_time:.1f}s for webhook quota")
                time.sleep(wait_time)

            return soonest[0]

        return best

    def stop(self):
        """停止池"""
        self.logger.info("Stopping WebhookPool")
        self._stop_flag.set()
        self.scheduler_thread.join(timeout=5)

    def __del__(self):
        """析构函数"""
        if hasattr(self, '_stop_flag') and not self._stop_flag.is_set():
            self.stop()
