"""
常量定义 - 向后兼容模块

此模块保持向后兼容，合并 core.constants 和企微特定常量
"""

# 从核心模块导入通用常量
from wecom_notifier.core.constants import (
    # 频率限制
    DEFAULT_RATE_LIMIT,
    DEFAULT_TIME_WINDOW,
    # 分段设置
    DEFAULT_SEGMENT_INTERVAL,
    # 重试设置
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_BACKOFF_FACTOR,
    # HTTP设置
    DEFAULT_TIMEOUT,
    # Markdown语法标记
    MARKDOWN_LINK_PATTERN,
    MARKDOWN_IMAGE_PATTERN,
    MARKDOWN_CODE_BLOCK_PATTERN,
    MARKDOWN_TABLE_ROW_PATTERN,
    # 页码格式设置
    PAGE_INDICATOR_FORMAT,
    MAX_PAGE_INDICATOR_BYTES,
    # 通用消息类型
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN,
)

# ===== 企业微信特定常量 =====

# 消息类型
MSG_TYPE_MARKDOWN_V2 = "markdown_v2"  # 企微特有
MSG_TYPE_IMAGE = "image"

# 分段设置（企微特定）
MAX_BYTES_PER_MESSAGE = 3800  # 每条消息最大字节数（留安全余量，实际限制4096）

# 服务端频控重试设置
RATE_LIMIT_MAX_RETRIES = 5  # 服务端频控最大重试次数
RATE_LIMIT_WAIT_TIME = 65  # 服务端频控等待时间（秒），略大于60秒以确保安全

# 企业微信API错误码
ERRCODE_SUCCESS = 0  # 成功
ERRCODE_WEBHOOK_INVALID = 93000  # webhook不存在
ERRCODE_RATE_LIMIT = 45009  # 频率限制
