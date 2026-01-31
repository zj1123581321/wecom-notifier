"""
wecom_notifier.platforms.wecom - 企业微信平台模块

提供企业微信的消息发送能力，包括：
- WeComNotifier: 企微通知器主类
- Sender: HTTP 发送器
- WebhookManager: 单 webhook 管理器
- WebhookResource: webhook 资源封装
- WeComWebhookPool: 多 webhook 池

使用示例：
    from wecom_notifier.platforms.wecom import WeComNotifier

    notifier = WeComNotifier()
    result = notifier.send_text("https://...", "Hello!")
    result.wait()
"""

# 主类
from wecom_notifier.platforms.wecom.notifier import WeComNotifier

# 发送器
from wecom_notifier.platforms.wecom.sender import Sender, RetryConfig

# 管理器
from wecom_notifier.platforms.wecom.manager import WebhookManager

# 资源
from wecom_notifier.platforms.wecom.resource import WebhookResource

# 池
from wecom_notifier.platforms.wecom.pool import WeComWebhookPool

# 适配器
from wecom_notifier.platforms.wecom.adapter import (
    WeComSenderAdapter,
    WeComMessageConverter,
)

# 模型
from wecom_notifier.platforms.wecom.models import Message

# 异常
from wecom_notifier.platforms.wecom.exceptions import (
    WeComError,
    NetworkError,
    WebhookInvalidError,
    RateLimitError,
    SegmentError,
    InvalidParameterError,
)

# 常量
from wecom_notifier.platforms.wecom.constants import (
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN,
    MSG_TYPE_MARKDOWN_V2,
    MSG_TYPE_IMAGE,
    MAX_BYTES_PER_MESSAGE,
    ERRCODE_SUCCESS,
    ERRCODE_WEBHOOK_INVALID,
    ERRCODE_RATE_LIMIT,
)

__all__ = [
    # 主类
    "WeComNotifier",
    # 发送器
    "Sender",
    "RetryConfig",
    # 管理器
    "WebhookManager",
    # 资源
    "WebhookResource",
    # 池
    "WeComWebhookPool",
    # 适配器
    "WeComSenderAdapter",
    "WeComMessageConverter",
    # 模型
    "Message",
    # 异常
    "WeComError",
    "NetworkError",
    "WebhookInvalidError",
    "RateLimitError",
    "SegmentError",
    "InvalidParameterError",
    # 常量
    "MSG_TYPE_TEXT",
    "MSG_TYPE_MARKDOWN",
    "MSG_TYPE_MARKDOWN_V2",
    "MSG_TYPE_IMAGE",
    "MAX_BYTES_PER_MESSAGE",
    "ERRCODE_SUCCESS",
    "ERRCODE_WEBHOOK_INVALID",
    "ERRCODE_RATE_LIMIT",
]
