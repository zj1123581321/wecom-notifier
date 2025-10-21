"""
企业微信通知器

一个功能完善的企业微信机器人通知组件，支持：
- 多种消息格式（text、markdown_v2、image）
- 频率控制（20条/分钟）
- 长文本自动分段
- 同步/异步发送
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

__version__ = "0.1.4"
__all__ = [
    "WeComNotifier",
    "SendResult",
    "WeComError",
    "NetworkError",
    "WebhookInvalidError",
    "RateLimitError",
    "InvalidParameterError"
]
