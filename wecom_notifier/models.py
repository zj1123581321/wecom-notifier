"""
数据模型 - 向后兼容模块

此模块保持向后兼容：
- Message: 企微特定实现，从 platforms.wecom.models 导入
- SendResult, SegmentInfo: 通用模型，从 core.models 导入
"""
from wecom_notifier.core.models import SendResult, SegmentInfo
from wecom_notifier.platforms.wecom.models import Message

__all__ = ["Message", "SendResult", "SegmentInfo"]
