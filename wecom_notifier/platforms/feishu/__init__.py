"""
wecom_notifier.platforms.feishu - 飞书平台模块

提供飞书的消息发送能力，包括：
- FeishuNotifier: 飞书通知器主类
- FeishuSender: HTTP 发送器
- FeishuSenderAdapter: 协议适配器
- DualRateLimiter: 双层频率控制器

使用示例:
    from wecom_notifier.platforms.feishu import FeishuNotifier

    notifier = FeishuNotifier()
    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

    # 发送文本
    result = notifier.send_text(webhook, "Hello!")
    result.wait()

    # 发送卡片
    result = notifier.send_card(webhook, "# 标题\\n内容", title="通知")
    result.wait()
"""

from wecom_notifier.platforms.feishu.notifier import FeishuNotifier, FeishuMessage
from wecom_notifier.platforms.feishu.sender import FeishuSender, FeishuRetryConfig
from wecom_notifier.platforms.feishu.adapter import (
    FeishuSenderAdapter,
    FeishuMessageConverter,
)
from wecom_notifier.platforms.feishu.rate_limiter import DualRateLimiter
from wecom_notifier.platforms.feishu.exceptions import (
    FeishuError,
    FeishuNetworkError,
    FeishuRateLimitError,
    FeishuKeywordError,
    FeishuIPError,
    FeishuSignError,
    FeishuBadRequestError,
)

__all__ = [
    # 主类
    "FeishuNotifier",
    "FeishuMessage",
    # 发送器
    "FeishuSender",
    "FeishuRetryConfig",
    # 适配器
    "FeishuSenderAdapter",
    "FeishuMessageConverter",
    # 频率控制
    "DualRateLimiter",
    # 异常
    "FeishuError",
    "FeishuNetworkError",
    "FeishuRateLimitError",
    "FeishuKeywordError",
    "FeishuIPError",
    "FeishuSignError",
    "FeishuBadRequestError",
]
