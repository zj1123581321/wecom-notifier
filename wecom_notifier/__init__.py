"""
企业微信通知器

一个功能完善的企业微信机器人通知组件，支持：
- 多种消息格式（text、markdown_v2、image）
- 频率控制（20条/分钟）
- 长文本自动分段
- 同步/异步发送

日志配置：
    本库默认不配置日志，由用户控制。详见 README.md 的日志配置章节。
"""

from .notifier import WeComNotifier
from .models import SendResult
from .exceptions import (
    WeComError,
    NetworkError,
    WebhookInvalidError,
    RateLimitError,
    InvalidParameterError
)
from .logger import setup_logger, disable_logger, enable_logger

__version__ = "0.2.0"
__all__ = [
    "WeComNotifier",
    "SendResult",
    "WeComError",
    "NetworkError",
    "WebhookInvalidError",
    "RateLimitError",
    "InvalidParameterError",
    # 日志工具
    "setup_logger",
    "disable_logger",
    "enable_logger"
]
