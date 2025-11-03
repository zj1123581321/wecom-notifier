"""
企业微信通知器 - 主类
"""
import hashlib
from typing import Optional, List, Dict, Union

from .logger import get_logger
from .constants import (
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN_V2,
    MSG_TYPE_IMAGE,
    DEFAULT_SEGMENT_INTERVAL
)
from .models import Message, SendResult
from .rate_limiter import RateLimiter
from .segmenter import MessageSegmenter
from .sender import Sender, RetryConfig
from .webhook_manager import WebhookManager
from .webhook_pool import WebhookPool
from .webhook_resource import WebhookResource
from .exceptions import InvalidParameterError
from .content_moderator import ContentModerator


class WeComNotifier:
    """
    企业微信通知器

    提供统一的接口来发送企业微信通知，支持：
    - 多webhook并发管理
    - 频率控制（20条/分钟）
    - 长文本自动分段
    - 同步/异步发送

    日志说明：
        本库使用 loguru 进行日志记录，库名为 'wecom_notifier'。
        默认情况下不会配置任何日志处理器，由用户在应用层统一配置。

        配置方式：
        1. 使用本库提供的工具（快速配置）：
           from wecom_notifier.logger import setup_logger
           setup_logger(log_level="INFO")

        2. 在应用层统一配置（推荐）：
           from loguru import logger
           logger.add("app.log", filter=lambda r: r["extra"].get("library") == "wecom_notifier")

        3. 完全静默：
           from wecom_notifier.logger import disable_logger
           disable_logger()
    """

    def __init__(
            self,
            max_retries: int = 3,
            retry_delay: float = 2.0,
            enable_content_moderation: bool = False,
            moderation_config: Optional[Dict] = None
    ):
        """
        初始化通知器

        Args:
            max_retries: HTTP请求最大重试次数
            retry_delay: 重试延迟（秒）
            enable_content_moderation: 是否启用内容审核
            moderation_config: 审核配置字典
                - sensitive_word_urls: List[str] - 敏感词URL列表
                - strategy: str - 审核策略 ("block" | "replace" | "pinyin_reverse")
                - cache_dir: str - 缓存目录（默认 ".wecom_cache"）
                - url_timeout: int - URL请求超时（秒，默认10）
                - log_sensitive_messages: bool - 是否记录敏感消息日志（默认True）
                - log_file: str - 日志文件路径（默认 ".wecom_cache/moderation.log"）
                - log_max_bytes: int - 单个日志文件最大字节数（默认10MB）
                - log_backup_count: int - 保留的备份文件数量（默认5）
        """
        # 获取库专属的 logger
        self.logger = get_logger()

        # 重试配置
        self.retry_config = RetryConfig(max_retries=max_retries, retry_delay=retry_delay)

        # 组件
        self.sender = Sender(retry_config=self.retry_config)
        self.segmenter = MessageSegmenter()

        # 全局RateLimiter字典（URL → RateLimiter映射）
        # 确保同一个URL在单webhook和多webhook模式下共享同一个限制器
        self.rate_limiters: Dict[str, RateLimiter] = {}

        # Webhook管理器字典（单webhook模式）
        self.webhook_managers: Dict[str, WebhookManager] = {}

        # Webhook池字典（多webhook模式）
        self.webhook_pools: Dict[str, WebhookPool] = {}

        # 内容审核器（可选）
        self.content_moderator: Optional[ContentModerator] = None
        if enable_content_moderation:
            if not moderation_config:
                self.logger.warning("Content moderation enabled but no config provided, using defaults")
                moderation_config = {}
            try:
                self.content_moderator = ContentModerator(moderation_config)
                if self.content_moderator.enabled:
                    self.logger.info("Content moderation enabled")
                else:
                    self.logger.warning("Content moderation initialized but disabled due to missing sensitive words")
            except Exception as e:
                self.logger.error(f"Failed to initialize content moderator: {e}")
                self.content_moderator = None

        self.logger.info("WeComNotifier initialized")

    def send_text(
            self,
            webhook_url: Union[str, List[str]],
            content: str,
            mentioned_list: Optional[List[str]] = None,
            mentioned_mobile_list: Optional[List[str]] = None,
            async_send: bool = True
    ) -> SendResult:
        """
        发送文本消息

        Args:
            webhook_url: Webhook地址（单个URL或URL列表）
            content: 文本内容
            mentioned_list: @的用户ID列表（如 ["user1", "@all"]）
            mentioned_mobile_list: @的手机号列表
            async_send: 是否异步发送（默认True）

        Returns:
            SendResult: 发送结果对象
        """
        message = Message(
            content=content,
            msg_type=MSG_TYPE_TEXT,
            mentioned_list=mentioned_list,
            mentioned_mobile_list=mentioned_mobile_list
        )

        return self._send_message(webhook_url, message, async_send)

    def send_markdown(
            self,
            webhook_url: Union[str, List[str]],
            content: str,
            mention_all: bool = False,
            async_send: bool = True
    ) -> SendResult:
        """
        发送Markdown v2消息

        Args:
            webhook_url: Webhook地址（单个URL或URL列表）
            content: Markdown内容
            mention_all: 是否@所有人（会额外发送一条text消息）
            async_send: 是否异步发送（默认True）

        Returns:
            SendResult: 发送结果对象
        """
        message = Message(
            content=content,
            msg_type=MSG_TYPE_MARKDOWN_V2,
            mention_all=mention_all
        )

        return self._send_message(webhook_url, message, async_send)

    def send_image(
            self,
            webhook_url: Union[str, List[str]],
            image_path: Optional[str] = None,
            image_base64: Optional[str] = None,
            mention_all: bool = False,
            async_send: bool = True
    ) -> SendResult:
        """
        发送图片消息

        Args:
            webhook_url: Webhook地址（单个URL或URL列表）
            image_path: 图片文件路径
            image_base64: 图片base64编码（二选一）
            mention_all: 是否@所有人（会额外发送一条text消息）
            async_send: 是否异步发送（默认True）

        Returns:
            SendResult: 发送结果对象

        Raises:
            InvalidParameterError: 参数错误
        """
        # 准备图片数据
        base64_data, md5_value = Sender.prepare_image(image_path, image_base64)

        message = Message(
            content=(base64_data, md5_value),
            msg_type=MSG_TYPE_IMAGE,
            mention_all=mention_all
        )

        return self._send_message(webhook_url, message, async_send)

    def _send_message(
            self,
            webhook_url: Union[str, List[str]],
            message: Message,
            async_send: bool
    ) -> SendResult:
        """
        发送消息（内部方法）

        Args:
            webhook_url: Webhook地址（单个或列表）
            message: 消息对象
            async_send: 是否异步发送

        Returns:
            SendResult: 发送结果对象
        """
        # 根据类型选择模式
        if isinstance(webhook_url, str):
            # 单webhook模式
            return self._send_single(webhook_url, message, async_send)
        elif isinstance(webhook_url, list):
            # 多webhook池模式
            if not webhook_url:
                raise InvalidParameterError("webhook_url list cannot be empty")
            return self._send_pool(webhook_url, message, async_send)
        else:
            raise InvalidParameterError("webhook_url must be str or list")

    def _send_single(self, webhook_url: str, message: Message, async_send: bool) -> SendResult:
        """
        单webhook模式发送

        Args:
            webhook_url: Webhook地址
            message: 消息对象
            async_send: 是否异步发送

        Returns:
            SendResult: 发送结果对象
        """
        # 获取或创建webhook管理器
        manager = self._get_or_create_manager(webhook_url)

        # 将消息加入队列
        result = manager.enqueue(message)

        # 如果是同步发送，等待结果
        if not async_send:
            result.wait()

        return result

    def _send_pool(self, webhook_urls: List[str], message: Message, async_send: bool) -> SendResult:
        """
        多webhook池模式发送

        Args:
            webhook_urls: Webhook地址列表
            message: 消息对象
            async_send: 是否异步发送

        Returns:
            SendResult: 发送结果对象
        """
        # 获取或创建池
        pool = self._get_or_create_pool(webhook_urls)

        # 将消息加入队列
        result = pool.enqueue(message)

        # 如果是同步发送，等待结果
        if not async_send:
            result.wait()

        return result

    def _get_or_create_manager(self, webhook_url: str) -> WebhookManager:
        """
        获取或创建Webhook管理器

        Args:
            webhook_url: Webhook地址

        Returns:
            WebhookManager: Webhook管理器
        """
        if webhook_url not in self.webhook_managers:
            # 获取或创建全局RateLimiter
            rate_limiter = self._get_or_create_rate_limiter(webhook_url)

            # 创建新的管理器
            manager = WebhookManager(
                webhook_url=webhook_url,
                sender=self.sender,
                segmenter=self.segmenter,
                rate_limiter=rate_limiter,
                content_moderator=self.content_moderator
            )
            self.webhook_managers[webhook_url] = manager

        return self.webhook_managers[webhook_url]

    def _get_or_create_rate_limiter(self, webhook_url: str) -> RateLimiter:
        """
        获取或创建全局RateLimiter（确保同一URL共享限制器）

        Args:
            webhook_url: Webhook地址

        Returns:
            RateLimiter: 频率限制器
        """
        if webhook_url not in self.rate_limiters:
            self.rate_limiters[webhook_url] = RateLimiter()

        return self.rate_limiters[webhook_url]

    def _get_or_create_pool(self, webhook_urls: List[str]) -> WebhookPool:
        """
        获取或创建Webhook池（带缓存）

        Args:
            webhook_urls: Webhook地址列表

        Returns:
            WebhookPool: Webhook池
        """
        # 生成池的唯一key
        pool_key = self._make_pool_key(webhook_urls)

        if pool_key not in self.webhook_pools:
            # 创建资源列表
            resources = []
            for url in webhook_urls:
                rate_limiter = self._get_or_create_rate_limiter(url)
                resource = WebhookResource(url, rate_limiter)
                resources.append(resource)

            # 创建池
            pool = WebhookPool(
                resources=resources,
                sender=self.sender,
                segmenter=self.segmenter,
                content_moderator=self.content_moderator
            )
            self.webhook_pools[pool_key] = pool

        return self.webhook_pools[pool_key]

    @staticmethod
    def _make_pool_key(webhook_urls: List[str]) -> str:
        """
        生成池的唯一key（排序后hash，确保顺序无关）

        Args:
            webhook_urls: Webhook地址列表

        Returns:
            str: 池的唯一key
        """
        sorted_urls = sorted(webhook_urls)
        key_string = "||".join(sorted_urls)
        return hashlib.md5(key_string.encode()).hexdigest()

    def stop_all(self):
        """停止所有Webhook管理器和池"""
        for manager in self.webhook_managers.values():
            manager.stop()

        for pool in self.webhook_pools.values():
            pool.stop()

    def __del__(self):
        """析构函数"""
        if hasattr(self, 'webhook_managers') or hasattr(self, 'webhook_pools'):
            self.stop_all()
