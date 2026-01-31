"""
频率限制器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.rate_limiter
"""
from wecom_notifier.core.rate_limiter import RateLimiter

__all__ = ["RateLimiter"]
