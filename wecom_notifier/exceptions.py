"""
自定义异常类 - 向后兼容模块

此模块保持向后兼容，合并 core.exceptions 和企微特定异常
"""

# 从核心模块导入通用异常
from wecom_notifier.core.exceptions import (
    NotificationError,
    NetworkError as CoreNetworkError,
    ConfigurationError,
    ModerationError,
    SegmentationError,
    RateLimitError as CoreRateLimitError,
)


# ===== 企业微信特定异常（向后兼容） =====

class WeComError(NotificationError):
    """企业微信通知基础异常"""
    pass


class NetworkError(WeComError):
    """网络相关错误"""
    pass


class WebhookInvalidError(WeComError):
    """Webhook地址无效"""
    pass


class RateLimitError(WeComError):
    """频率限制错误（服务端返回）"""
    pass


class SegmentError(WeComError):
    """分段发送错误"""

    def __init__(self, message, success_count=0, fail_count=0, errors=None):
        super().__init__(message)
        self.success_count = success_count
        self.fail_count = fail_count
        self.errors = errors or []


class InvalidParameterError(WeComError):
    """参数错误"""
    pass


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
