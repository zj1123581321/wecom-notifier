"""
企业微信通知器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.platforms.wecom.notifier
"""
from wecom_notifier.platforms.wecom.notifier import WeComNotifier

__all__ = ["WeComNotifier"]
