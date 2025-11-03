"""
常量定义
"""

# 消息类型
MSG_TYPE_TEXT = "text"
MSG_TYPE_MARKDOWN = "markdown"
MSG_TYPE_MARKDOWN_V2 = "markdown_v2"
MSG_TYPE_IMAGE = "image"

# 频率限制
DEFAULT_RATE_LIMIT = 20  # 每分钟最大消息数
DEFAULT_TIME_WINDOW = 60  # 时间窗口（秒）

# 分段设置
MAX_BYTES_PER_MESSAGE = 3800  # 每条消息最大字节数（留安全余量，实际限制4096）
DEFAULT_SEGMENT_INTERVAL = 1000  # 默认分段间隔（毫秒）

# 重试设置
DEFAULT_MAX_RETRIES = 3  # 默认最大重试次数（针对网络错误）
DEFAULT_RETRY_DELAY = 2.0  # 默认重试延迟（秒）
DEFAULT_BACKOFF_FACTOR = 2.0  # 指数退避因子

# 服务端频控重试设置
RATE_LIMIT_MAX_RETRIES = 5  # 服务端频控最大重试次数
RATE_LIMIT_WAIT_TIME = 65  # 服务端频控等待时间（秒），略大于60秒以确保安全

# HTTP设置
DEFAULT_TIMEOUT = 10  # HTTP请求超时（秒）

# 企业微信API错误码
ERRCODE_SUCCESS = 0  # 成功
ERRCODE_WEBHOOK_INVALID = 93000  # webhook不存在
ERRCODE_RATE_LIMIT = 45009  # 频率限制

# Markdown语法标记
MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'  # [文字](url)
MARKDOWN_IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'  # ![文字](url)
MARKDOWN_CODE_BLOCK_PATTERN = r'```[\s\S]*?```'  # 代码块
MARKDOWN_TABLE_ROW_PATTERN = r'^\|.*\|$'  # 表格行

# 页码格式设置
PAGE_INDICATOR_FORMAT = "(Page {current}/{total})\n"  # 页码格式
MAX_PAGE_INDICATOR_BYTES = 20  # 页码标记预留字节数
