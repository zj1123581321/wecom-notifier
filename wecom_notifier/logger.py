"""
日志系统 - 向后兼容模块

此模块保持向后兼容，实际实现已迁移到 wecom_notifier.core.logger
"""
from wecom_notifier.core.logger import (
    get_logger,
    setup_logger,
    disable_logger,
    enable_logger,
    _library_logger,
)

__all__ = [
    "get_logger",
    "setup_logger",
    "disable_logger",
    "enable_logger",
    "_library_logger",
]
