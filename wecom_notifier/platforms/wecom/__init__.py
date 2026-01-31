"""
wecom_notifier.platforms.wecom - 企业微信平台模块

提供企业微信的消息发送能力，包括：
- WeComSenderAdapter: 实现 SenderProtocol 的发送器适配器
- WeComMessageConverter: 实现 MessageConverterProtocol 的消息转换器
- WeComWebhookPool: 企微 Webhook 池实现

使用示例：
    from wecom_notifier.platforms.wecom import WeComSenderAdapter
    from wecom_notifier.sender import Sender

    sender = Sender()
    adapter = WeComSenderAdapter(sender)
    success, error = adapter.send(webhook_url, "text", "Hello", metadata)
"""

from wecom_notifier.platforms.wecom.adapter import (
    WeComSenderAdapter,
    WeComMessageConverter,
)
from wecom_notifier.platforms.wecom.pool import WeComWebhookPool

__all__ = [
    "WeComSenderAdapter",
    "WeComMessageConverter",
    "WeComWebhookPool",
]
