"""
敏感词加载器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.moderation.word_loader
"""
from wecom_notifier.core.moderation.word_loader import SensitiveWordLoader

__all__ = ["SensitiveWordLoader"]
