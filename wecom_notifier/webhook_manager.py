"""
Webhook管理器 - 管理单个webhook的消息队列和发送
"""
import logging
import queue
import threading
import time
from typing import Optional

from .models import Message, SendResult
from .rate_limiter import RateLimiter
from .segmenter import MessageSegmenter
from .sender import Sender, RetryConfig
from .constants import MSG_TYPE_TEXT, MSG_TYPE_MARKDOWN_V2, MSG_TYPE_IMAGE


class WebhookManager:
    """
    Webhook管理器

    为每个webhook维护独立的消息队列、频率限制器和发送线程
    """

    def __init__(
            self,
            webhook_url: str,
            sender: Sender,
            segmenter: MessageSegmenter,
            rate_limiter: RateLimiter,
            logger: Optional[logging.Logger] = None
    ):
        """
        初始化Webhook管理器

        Args:
            webhook_url: Webhook地址
            sender: HTTP发送器
            segmenter: 消息分段器
            rate_limiter: 频率限制器
            logger: 日志记录器
        """
        self.webhook_url = webhook_url
        self.sender = sender
        self.segmenter = segmenter
        self.rate_limiter = rate_limiter
        self.logger = logger or logging.getLogger(__name__)

        # 消息队列
        self.message_queue = queue.Queue()

        # 结果字典，用于存储SendResult
        self.results = {}

        # 停止标志（必须在启动线程前初始化）
        self._stop_flag = threading.Event()

        # 工作线程
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

        self.logger.info(f"WebhookManager initialized for {webhook_url}")

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

        self.logger.debug(f"Message {message.id} enqueued (type={message.msg_type})")
        return result

    def _process_queue(self):
        """处理消息队列的工作线程"""
        self.logger.info(f"Worker thread started for {self.webhook_url}")

        while not self._stop_flag.is_set():
            try:
                # 从队列获取消息（超时1秒，以便检查停止标志）
                message = self.message_queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                # 处理消息
                self._process_message(message)
            except Exception as e:
                self.logger.error(f"Error processing message {message.id}: {e}", exc_info=True)
                result = self.results.get(message.id)
                if result:
                    result.mark_failed(f"Internal error: {e}")
            finally:
                self.message_queue.task_done()

    def _process_message(self, message: Message):
        """
        处理单条消息

        Args:
            message: 消息对象
        """
        result = self.results.get(message.id)
        if not result:
            self.logger.error(f"Result not found for message {message.id}")
            return

        self.logger.info(f"Processing message {message.id} (type={message.msg_type})")

        # 分段
        segments = self._get_segments(message)
        total_segments = len(segments)

        self.logger.debug(f"Message {message.id} split into {total_segments} segments")

        # 发送每个分段
        for i, segment in enumerate(segments):
            # 频率控制
            self.rate_limiter.acquire()

            # 发送
            success, error = self._send_segment(message, segment.content, i)

            if not success:
                # 发送失败，立即停止
                self.logger.error(f"Segment {i + 1}/{total_segments} failed for message {message.id}: {error}")
                result.mark_failed(f"Segment {i + 1}/{total_segments} failed: {error}")
                return

            self.logger.debug(f"Segment {i + 1}/{total_segments} sent successfully for message {message.id}")

            # 分段间延迟（最后一个分段不需要延迟）
            if i < total_segments - 1:
                time.sleep(message.segment_interval / 1000.0)

        # 处理@all workaround（针对markdown_v2和image）
        if message.needs_mention_all_workaround():
            self.logger.debug(f"Sending @all workaround for message {message.id}")

            self.rate_limiter.acquire()
            success, error = self.sender.send_mention_all(self.webhook_url)

            if not success:
                self.logger.error(f"@all workaround failed for message {message.id}: {error}")
                result.mark_failed(f"@all workaround failed: {error}")
                return

        # 所有分段发送成功
        self.logger.info(f"Message {message.id} sent successfully ({total_segments} segments)")
        result.mark_success()

    def _get_segments(self, message: Message):
        """
        获取消息分段

        Args:
            message: 消息对象

        Returns:
            List[SegmentInfo]: 分段列表
        """
        # 对于图片类型，不需要分段
        if message.msg_type == MSG_TYPE_IMAGE:
            from .models import SegmentInfo
            return [SegmentInfo(message.content, is_first=True, is_last=True)]

        # 文本和Markdown需要分段
        return self.segmenter.segment(message.content, message.msg_type)

    def _send_segment(self, message: Message, content: str, segment_index: int) -> tuple:
        """
        发送单个分段

        Args:
            message: 消息对象
            content: 分段内容
            segment_index: 分段索引

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        if message.msg_type == MSG_TYPE_TEXT:
            return self.sender.send_text(
                self.webhook_url,
                content,
                mentioned_list=message.mentioned_list if segment_index == 0 else None,
                mentioned_mobile_list=message.mentioned_mobile_list if segment_index == 0 else None
            )

        elif message.msg_type == MSG_TYPE_MARKDOWN_V2:
            return self.sender.send_markdown(self.webhook_url, content)

        elif message.msg_type == MSG_TYPE_IMAGE:
            # 图片内容应该是 (base64, md5) 元组
            if isinstance(content, tuple) and len(content) == 2:
                base64_data, md5_value = content
                return self.sender.send_image(self.webhook_url, base64_data, md5_value)
            else:
                # content 应该是已经准备好的图片数据
                return self.sender.send_image(self.webhook_url, content[0], content[1])

        else:
            return False, f"Unsupported message type: {message.msg_type}"

    def stop(self):
        """停止管理器"""
        self.logger.info(f"Stopping WebhookManager for {self.webhook_url}")
        self._stop_flag.set()
        self.worker_thread.join(timeout=5)

    def __del__(self):
        """析构函数"""
        if hasattr(self, '_stop_flag') and not self._stop_flag.is_set():
            self.stop()
