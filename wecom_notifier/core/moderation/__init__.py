"""
wecom_notifier.core.moderation - 内容审核模块

此模块提供内容审核功能：
- ContentModerator: 内容审核器主类
- ContentFilter: AC自动机敏感词检测
- ModerationStrategy: 审核策略（Block/Replace/PinyinReverse）
- SensitiveWordLoader: 敏感词加载器
- SensitiveMessageLogger: 敏感消息日志
"""

from wecom_notifier.core.moderation.moderator import ContentModerator
from wecom_notifier.core.moderation.filter import ContentFilter, SensitiveWordMatch
from wecom_notifier.core.moderation.strategies import (
    ModerationStrategy,
    BlockStrategy,
    ReplaceStrategy,
    PinyinReverseStrategy,
    create_strategy,
)
from wecom_notifier.core.moderation.word_loader import SensitiveWordLoader
from wecom_notifier.core.moderation.sensitive_logger import SensitiveMessageLogger

__all__ = [
    # 审核器
    "ContentModerator",
    # 过滤器
    "ContentFilter",
    "SensitiveWordMatch",
    # 策略
    "ModerationStrategy",
    "BlockStrategy",
    "ReplaceStrategy",
    "PinyinReverseStrategy",
    "create_strategy",
    # 加载器
    "SensitiveWordLoader",
    # 日志
    "SensitiveMessageLogger",
]
