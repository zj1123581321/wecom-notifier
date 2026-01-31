"""
内容审核策略 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.moderation.strategies
"""
from wecom_notifier.core.moderation.strategies import (
    ModerationStrategy,
    BlockStrategy,
    ReplaceStrategy,
    PinyinReverseStrategy,
    create_strategy,
)

__all__ = [
    "ModerationStrategy",
    "BlockStrategy",
    "ReplaceStrategy",
    "PinyinReverseStrategy",
    "create_strategy",
]
