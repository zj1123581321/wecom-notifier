"""
企业微信平台异常定义
"""

from wecom_notifier.core.exceptions import NotificationError


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
    "WeComError",
    "NetworkError",
    "WebhookInvalidError",
    "RateLimitError",
    "SegmentError",
    "InvalidParameterError",
]
