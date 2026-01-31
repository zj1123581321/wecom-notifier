"""
自定义异常类 - 向后兼容模块

此模块保持向后兼容：
- 核心异常从 core.exceptions 导入
- 企微特定异常从 platforms.wecom.exceptions 导入
"""

# 从核心模块导入通用异常
from wecom_notifier.core.exceptions import (
    NotificationError,
    ConfigurationError,
    ModerationError,
    SegmentationError,
)

# 从企微平台导入企微特定异常
from wecom_notifier.platforms.wecom.exceptions import (
    WeComError,
    NetworkError,
    WebhookInvalidError,
    RateLimitError,
    SegmentError,
    InvalidParameterError,
)

__all__ = [
    # 核心异常
    "NotificationError",
    "ConfigurationError",
    "ModerationError",
    "SegmentationError",
    # 企微异常（向后兼容）
    "WeComError",
    "NetworkError",
    "WebhookInvalidError",
    "RateLimitError",
    "SegmentError",
    "InvalidParameterError",
]
