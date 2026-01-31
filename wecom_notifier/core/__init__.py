"""
wecom_notifier.core - 核心模块

此模块包含平台无关的核心功能：
- 协议定义 (SenderProtocol, RateLimiterProtocol, MessageConverterProtocol)
- 频率控制 (RateLimiter)
- 消息分段 (MessageSegmenter)
- 数据模型 (Message, SendResult, SegmentInfo)
- 日志系统 (logger utilities)
- 核心常量和异常
"""

from wecom_notifier.core.protocols import (
    SenderProtocol,
    RateLimiterProtocol,
    MessageConverterProtocol,
)
from wecom_notifier.core.rate_limiter import RateLimiter
from wecom_notifier.core.segmenter import MessageSegmenter
from wecom_notifier.core.models import Message, SendResult, SegmentInfo
from wecom_notifier.core.logger import get_logger, setup_logger, disable_logger, enable_logger
from wecom_notifier.core.exceptions import (
    NotificationError,
    NetworkError,
    ConfigurationError,
    ModerationError,
    SegmentationError,
)

__all__ = [
    # 协议
    "SenderProtocol",
    "RateLimiterProtocol",
    "MessageConverterProtocol",
    # 频率控制
    "RateLimiter",
    # 分段器
    "MessageSegmenter",
    # 数据模型
    "Message",
    "SendResult",
    "SegmentInfo",
    # 日志
    "get_logger",
    "setup_logger",
    "disable_logger",
    "enable_logger",
    # 异常
    "NotificationError",
    "NetworkError",
    "ConfigurationError",
    "ModerationError",
    "SegmentationError",
]
