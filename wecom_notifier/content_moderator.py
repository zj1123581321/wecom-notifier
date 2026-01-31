"""
内容审核器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.moderation.moderator
"""
from wecom_notifier.core.moderation.moderator import ContentModerator

__all__ = ["ContentModerator"]
