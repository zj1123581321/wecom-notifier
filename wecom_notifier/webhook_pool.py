"""
Webhook池 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到:
- core/pool_base.py (通用基类)
- platforms/wecom/pool.py (企微实现)
"""
from typing import List, Optional, TYPE_CHECKING

from wecom_notifier.platforms.wecom.pool import WeComWebhookPool
from wecom_notifier.core.pool_base import AllWebhooksUnavailableError
from wecom_notifier.core.segmenter import MessageSegmenter
from wecom_notifier.platforms.wecom.sender import Sender
from wecom_notifier.platforms.wecom.resource import WebhookResource

if TYPE_CHECKING:
    from wecom_notifier.core.moderation import ContentModerator


# 向后兼容：重新导出异常
__all__ = ["WebhookPool", "AllWebhooksUnavailableError"]


class WebhookPool(WeComWebhookPool):
    """
    Webhook池 - 向后兼容包装类

    管理多个webhook的负载均衡发送：
    - 全局消息队列（保证顺序）
    - 单线程调度器（串行处理）
    - 智能webhook选择（最空闲优先）
    - 自动容错和恢复

    此类继承自 WeComWebhookPool，保持原有 API 完全兼容。
    """

    def __init__(
        self,
        resources: List[WebhookResource],
        sender: Sender,
        segmenter: MessageSegmenter,
        content_moderator: Optional["ContentModerator"] = None
    ):
        """
        初始化Webhook池

        Args:
            resources: Webhook资源列表
            sender: HTTP发送器
            segmenter: 消息分段器
            content_moderator: 内容审核器（可选）
        """
        super().__init__(
            resources=resources,
            sender=sender,
            segmenter=segmenter,
            content_moderator=content_moderator
        )
