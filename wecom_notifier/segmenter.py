"""
消息分段器 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.segmenter
"""
from wecom_notifier.core.segmenter import MessageSegmenter

__all__ = ["MessageSegmenter"]
