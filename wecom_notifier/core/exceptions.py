"""
核心异常定义 - 平台无关
"""


class NotificationError(Exception):
    """通知库基础异常"""
    pass


class NetworkError(NotificationError):
    """网络错误（超时、连接失败）"""
    pass


class ConfigurationError(NotificationError):
    """配置错误"""
    pass


class ModerationError(NotificationError):
    """内容审核错误"""
    pass


class SegmentationError(NotificationError):
    """分段错误"""

    def __init__(self, message, success_count=0, fail_count=0, errors=None):
        super().__init__(message)
        self.success_count = success_count
        self.fail_count = fail_count
        self.errors = errors or []


class RateLimitError(NotificationError):
    """频率限制错误（服务端返回）"""
    pass
