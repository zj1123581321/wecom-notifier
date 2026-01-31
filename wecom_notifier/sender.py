"""
HTTP发送器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.platforms.wecom.sender
"""
from wecom_notifier.platforms.wecom.sender import Sender, RetryConfig

__all__ = ["Sender", "RetryConfig"]
