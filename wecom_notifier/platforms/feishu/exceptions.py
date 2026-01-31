"""
飞书平台异常定义
"""
from wecom_notifier.core.exceptions import NotificationError, NetworkError


class FeishuError(NotificationError):
    """飞书平台基础异常"""
    pass


class FeishuNetworkError(FeishuError, NetworkError):
    """飞书网络错误（超时、连接失败）"""
    pass


class FeishuRateLimitError(FeishuError):
    """飞书频率限制错误（错误码 11232）"""
    pass


class FeishuKeywordError(FeishuError):
    """飞书关键词校验失败（错误码 19024）"""
    pass


class FeishuIPError(FeishuError):
    """飞书 IP 白名单校验失败（错误码 19022）"""
    pass


class FeishuSignError(FeishuError):
    """飞书签名校验失败（错误码 19021）"""
    pass


class FeishuBadRequestError(FeishuError):
    """飞书请求格式错误（错误码 9499）"""
    pass


__all__ = [
    "FeishuError",
    "FeishuNetworkError",
    "FeishuRateLimitError",
    "FeishuKeywordError",
    "FeishuIPError",
    "FeishuSignError",
    "FeishuBadRequestError",
]
