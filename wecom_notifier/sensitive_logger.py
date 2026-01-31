"""
敏感消息日志记录器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.moderation.sensitive_logger
"""
from wecom_notifier.core.moderation.sensitive_logger import SensitiveMessageLogger

__all__ = ["SensitiveMessageLogger"]
