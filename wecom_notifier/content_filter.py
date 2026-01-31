"""
内容过滤器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.moderation.filter
"""
from wecom_notifier.core.moderation.filter import ContentFilter, SensitiveWordMatch

__all__ = ["ContentFilter", "SensitiveWordMatch"]
