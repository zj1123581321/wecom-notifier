"""
企业微信通知器 - 主类
"""
import logging
from typing import Optional, List, Dict

from .constants import (
    DEFAULT_LOG_LEVEL,
    LOG_FORMAT,
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
from .exceptions import InvalidParameterError


class WeComNotifier:
    """
    企业微信通知器

    提供统一的接口来发送企业微信通知，支持：
    - 多webhook并发管理
    - 频率控制（20条/分钟）
    - 长文本自动分段
    - 同步/异步发送
    """

    def __init__(
            self,
            max_retries: int = 3,
            retry_delay: float = 2.0,
            log_level: str = DEFAULT_LOG_LEVEL,
            logger: Optional[logging.Logger] = None
    ):
        """
        初始化通知器

        Args:
            max_retries: HTTP请求最大重试次数
            retry_delay: 重试延迟（秒）
            log_level: 日志级别
            logger: 自定义日志记录器
        """
        # 配置日志
        self.logger = logger or self._setup_logger(log_level)

        # 重试配置
        self.retry_config = RetryConfig(max_retries=max_retries, retry_delay=retry_delay)

        # 组件
        self.sender = Sender(retry_config=self.retry_config, logger=self.logger)
        self.segmenter = MessageSegmenter()

        # Webhook管理器字典
        self.webhook_managers: Dict[str, WebhookManager] = {}

        self.logger.info("WeComNotifier initialized")

    def send_text(
            self,
            webhook_url: str,
            content: str,
            mentioned_list: Optional[List[str]] = None,
            mentioned_mobile_list: Optional[List[str]] = None,
            async_send: bool = True
    ) -> SendResult:
        """
        发送文本消息

        Args:
            webhook_url: Webhook地址
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
            webhook_url: str,
            content: str,
            mention_all: bool = False,
            async_send: bool = True
    ) -> SendResult:
        """
        发送Markdown v2消息

        Args:
            webhook_url: Webhook地址
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
            webhook_url: str,
            image_path: Optional[str] = None,
            image_base64: Optional[str] = None,
            mention_all: bool = False,
            async_send: bool = True
    ) -> SendResult:
        """
        发送图片消息

        Args:
            webhook_url: Webhook地址
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

    def _send_message(self, webhook_url: str, message: Message, async_send: bool) -> SendResult:
        """
        发送消息（内部方法）

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

    def _get_or_create_manager(self, webhook_url: str) -> WebhookManager:
        """
        获取或创建Webhook管理器

        Args:
            webhook_url: Webhook地址

        Returns:
            WebhookManager: Webhook管理器
        """
        if webhook_url not in self.webhook_managers:
            # 创建新的管理器
            rate_limiter = RateLimiter()
            manager = WebhookManager(
                webhook_url=webhook_url,
                sender=self.sender,
                segmenter=self.segmenter,
                rate_limiter=rate_limiter,
                logger=self.logger
            )
            self.webhook_managers[webhook_url] = manager

        return self.webhook_managers[webhook_url]

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """
        设置日志记录器

        Args:
            log_level: 日志级别

        Returns:
            logging.Logger: 日志记录器
        """
        logger = logging.getLogger('wecom_notifier')
        logger.setLevel(getattr(logging, log_level.upper()))

        # 避免重复添加handler
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(LOG_FORMAT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def stop_all(self):
        """停止所有Webhook管理器"""
        for manager in self.webhook_managers.values():
            manager.stop()

    def __del__(self):
        """析构函数"""
        if hasattr(self, 'webhook_managers'):
            self.stop_all()
