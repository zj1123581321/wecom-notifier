"""
Webhook资源 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.platforms.wecom.resource
"""
from wecom_notifier.platforms.wecom.resource import WebhookResource

__all__ = ["WebhookResource"]
