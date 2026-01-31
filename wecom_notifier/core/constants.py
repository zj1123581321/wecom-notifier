"""
核心常量 - 平台无关配置
"""

# 频率限制（通用默认值）
DEFAULT_RATE_LIMIT = 20  # 每分钟最大消息数
DEFAULT_TIME_WINDOW = 60  # 时间窗口（秒）

# 分段设置
DEFAULT_SEGMENT_INTERVAL = 1000  # 默认分段间隔（毫秒）

# 重试设置
DEFAULT_MAX_RETRIES = 3  # 默认最大重试次数（针对网络错误）
DEFAULT_RETRY_DELAY = 2.0  # 默认重试延迟（秒）
DEFAULT_BACKOFF_FACTOR = 2.0  # 指数退避因子

# HTTP设置
DEFAULT_TIMEOUT = 10  # HTTP请求超时（秒）

# Markdown语法标记（通用）
MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'  # [文字](url)
MARKDOWN_IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'  # ![文字](url)
MARKDOWN_CODE_BLOCK_PATTERN = r'```[\s\S]*?```'  # 代码块
MARKDOWN_TABLE_ROW_PATTERN = r'^\|.*\|$'  # 表格行

# 页码格式设置
PAGE_INDICATOR_FORMAT = "(Page {current}/{total})\n"  # 页码格式
MAX_PAGE_INDICATOR_BYTES = 20  # 页码标记预留字节数

# 消息类型（通用）
MSG_TYPE_TEXT = "text"
MSG_TYPE_MARKDOWN = "markdown"  # 通用Markdown类型
