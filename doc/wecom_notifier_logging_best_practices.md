# wecom-notifier 日志系统改进建议

## 问题描述

当前 `wecom-notifier` (v0.1.5) 在初始化时会强制重置全局日志配置：

```python
class WeComNotifier:
    def __init__(self, ..., log_level: str = DEFAULT_LOG_LEVEL):
        # 配置日志
        self._setup_logger(log_level)
        ...

    def _setup_logger(self, log_level: str):
        # 移除默认的 handler
        logger.remove()  # ❌ 移除了所有 handler，包括应用程序配置的

        # 添加自定义格式的 handler
        logger.add(
            sys.stdout,  # ❌ 只添加控制台输出
            format="...",
            level=log_level.upper(),
            colorize=True
        )
```

**问题影响：**

1. **破坏性行为**：`logger.remove()` 会移除应用程序预先配置的所有日志处理器（如文件输出、远程日志等）
2. **控制权丧失**：应用程序无法控制库的日志行为
3. **违反最小惊讶原则**：用户不期望导入一个库会修改全局日志配置
4. **无法集成**：与已有日志系统难以集成

---

## 第三方库日志系统最佳实践

### 原则 1：使用独立的 Logger 实例

**不推荐：** 使用全局 `logger`

```python
from loguru import logger  # 全局实例

logger.info("...")  # 影响所有使用 loguru 的代码
```

**推荐：** 创建库专属的 logger

```python
from loguru import logger
import sys

# 创建库专属的 logger 实例
_logger = logger.bind(name="wecom_notifier")

class WeComNotifier:
    def __init__(self):
        # 不要配置全局 logger
        self.logger = _logger
```

### 原则 2：不在 `__init__` 中配置日志

**不推荐：** 自动配置日志

```python
class WeComNotifier:
    def __init__(self, log_level: str = "INFO"):
        self._setup_logger(log_level)  # ❌ 强制配置
```

**推荐：** 让用户决定是否配置

```python
class WeComNotifier:
    def __init__(self, configure_logging: bool = False, log_level: str = "INFO"):
        """
        Args:
            configure_logging: 是否自动配置日志（默认False）
            log_level: 日志级别（仅在 configure_logging=True 时生效）
        """
        if configure_logging:
            self.setup_logger(log_level)
```

### 原则 3：提供可选的日志配置方法

```python
class WeComNotifier:
    @staticmethod
    def setup_logger(
        log_level: str = "INFO",
        add_console: bool = True,
        add_file: bool = False,
        log_file: Optional[Path] = None
    ):
        """
        可选的日志配置方法（用户显式调用）

        Args:
            log_level: 日志级别
            add_console: 是否添加控制台输出
            add_file: 是否添加文件输出
            log_file: 日志文件路径
        """
        # 只配置 wecom_notifier 的 logger，不影响全局
        if add_console:
            _logger.add(
                sys.stdout,
                format="...",
                level=log_level.upper(),
                filter=lambda record: record["name"] == "wecom_notifier"
            )

        if add_file and log_file:
            _logger.add(
                log_file,
                format="...",
                level=log_level.upper(),
                filter=lambda record: record["name"] == "wecom_notifier"
            )
```

### 原则 4：遵守日志级别控制

用户应该能够通过标准方式控制库的日志输出：

```python
# 用户代码
import logging

# 方式 1：通过标准 logging 模块
logging.getLogger("wecom_notifier").setLevel(logging.WARNING)

# 方式 2：通过 loguru 环境变量
# export LOGURU_LEVEL=WARNING

# 方式 3：通过 loguru API
from loguru import logger
logger.disable("wecom_notifier")  # 完全禁用
logger.enable("wecom_notifier")   # 重新启用
```

---

## 推荐的改进方案

### 方案 A：最小侵入式改进（向后兼容）

```python
# wecom_notifier/notifier.py

from loguru import logger
import sys
from typing import Optional

# 创建库专属的 logger
_logger = logger.bind(name="wecom_notifier")


class WeComNotifier:
    """
    企业微信通知器

    日志说明：
        默认情况下，本库不会配置任何日志处理器。
        如需配置，请调用 WeComNotifier.setup_logger() 方法，
        或在初始化时传入 configure_logging=True。
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        configure_logging: bool = False,  # 新增参数，默认不配置
        log_level: str = "INFO"
    ):
        """
        初始化通知器

        Args:
            max_retries: HTTP请求最大重试次数
            retry_delay: 重试延迟（秒）
            configure_logging: 是否自动配置日志（默认False，不影响应用程序日志配置）
            log_level: 日志级别（仅在 configure_logging=True 时生效）
        """
        # 使用库专属的 logger
        self.logger = _logger

        # 只在用户明确要求时才配置日志
        if configure_logging:
            self.setup_logger(log_level)

        # 其余初始化代码...
        self.retry_config = RetryConfig(max_retries=max_retries, retry_delay=retry_delay)
        self.sender = Sender(retry_config=self.retry_config)
        self.segmenter = MessageSegmenter()

        self.logger.info("WeComNotifier initialized")

    @staticmethod
    def setup_logger(
        log_level: str = "INFO",
        add_console: bool = True,
        console_format: Optional[str] = None,
        add_file: bool = False,
        log_file: Optional[str] = None,
        file_format: Optional[str] = None
    ):
        """
        配置 wecom-notifier 的日志系统

        注意：此方法不会影响应用程序的其他日志配置

        Args:
            log_level: 日志级别
            add_console: 是否添加控制台输出
            console_format: 控制台日志格式
            add_file: 是否添加文件输出
            log_file: 日志文件路径
            file_format: 文件日志格式
        """
        if console_format is None:
            console_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )

        if file_format is None:
            file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

        # 只添加针对 wecom_notifier 的处理器
        if add_console:
            _logger.add(
                sys.stdout,
                format=console_format,
                level=log_level.upper(),
                colorize=True,
                filter=lambda record: record["extra"].get("name") == "wecom_notifier"
            )

        if add_file and log_file:
            _logger.add(
                log_file,
                format=file_format,
                level=log_level.upper(),
                encoding="utf-8",
                rotation="10 MB",
                retention="7 days",
                filter=lambda record: record["extra"].get("name") == "wecom_notifier"
            )
```

**使用方式：**

```python
# 方式 1：让应用程序完全控制日志（推荐）
from wecom_notifier import WeComNotifier

notifier = WeComNotifier(
    max_retries=5,
    retry_delay=2.0
    # 不传 configure_logging，库不会配置日志
)
# 应用程序的日志配置不受影响

# 方式 2：使用库的日志配置
notifier = WeComNotifier(
    max_retries=5,
    retry_delay=2.0,
    configure_logging=True,  # 显式要求配置日志
    log_level="INFO"
)

# 方式 3：手动配置库的日志
WeComNotifier.setup_logger(
    log_level="DEBUG",
    add_console=True,
    add_file=True,
    log_file="wecom.log"
)
notifier = WeComNotifier()
```

### 方案 B：完全解耦（破坏性变更）

如果可以接受破坏性变更，建议：

1. **完全移除自动日志配置**
2. **在文档中说明日志配置要求**
3. **提供独立的日志配置工具**

```python
class WeComNotifier:
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """
        初始化通知器

        日志说明：
            本库使用 loguru 进行日志记录，logger 名称为 'wecom_notifier'。
            请在应用程序中配置日志系统，例如：

            from loguru import logger
            logger.add("app.log", filter=lambda r: "wecom_notifier" in r["name"])
        """
        self.logger = logger.bind(name="wecom_notifier")
        # 不再配置日志
        self.logger.info("WeComNotifier initialized")
```

---

## 迁移指南

### 现有用户

如果当前依赖库自动配置日志的行为：

```python
# 旧代码
notifier = WeComNotifier(log_level="INFO")

# 新代码（方案A）
WeComNotifier.setup_logger(log_level="INFO")  # 显式配置
notifier = WeComNotifier()

# 或
notifier = WeComNotifier(configure_logging=True, log_level="INFO")
```

### 新用户（应用程序已有日志系统）

```python
# 应用程序配置日志
from loguru import logger
logger.add("app.log", level="INFO")

# 使用库（不配置日志）
from wecom_notifier import WeComNotifier
notifier = WeComNotifier()  # 自动使用应用程序的日志配置
```

---

## 参考资料

### 第三方库日志最佳实践

1. **Python 官方建议**：
   - [Logging HOWTO](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library)
   - 库不应配置根 logger
   - 使用 `NullHandler` 作为默认处理器

2. **requests 库的做法**：
   ```python
   import logging
   # 创建库专属 logger
   logger = logging.getLogger(__name__)
   # 添加 NullHandler（不输出）
   logger.addHandler(logging.NullHandler())
   ```

3. **loguru 官方建议**：
   - [Library Usage](https://loguru.readthedocs.io/en/stable/resources/recipes.html#using-loguru-s-logger-within-a-library)
   - 让用户控制日志配置
   - 使用 `logger.bind()` 创建库专属实例

### 实施优先级

1. **高优先级**（必须修改）：
   - 移除 `logger.remove()` 调用
   - 将 `configure_logging` 参数默认值改为 `False`

2. **中优先级**（强烈建议）：
   - 使用库专属的 logger 实例
   - 提供 `setup_logger()` 静态方法

3. **低优先级**（锦上添花）：
   - 详细的日志配置文档
   - 日志级别动态调整 API

---

## 总结

**核心原则：** 第三方库应该是 **"好市民"**，不应该干涉应用程序的全局配置。

**改进收益：**
- ✅ 不破坏应用程序的日志配置
- ✅ 用户可以完全控制日志行为
- ✅ 更容易集成到现有系统
- ✅ 符合 Python 社区最佳实践
- ✅ 向后兼容（方案A）

**建议优先采用方案A**，保持向后兼容的同时提供更好的控制能力。
