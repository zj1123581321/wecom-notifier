# wecom-notifier 日志配置指南

本文档详细说明了如何配置 wecom-notifier 的日志系统。

## 设计理念

**v0.2.0+ 重大变更**：本库不再自动配置日志，遵循第三方库最佳实践。

### 核心原则

1. ✅ **库不配置日志** - 默认情况下不会修改任何日志配置
2. ✅ **用户完全控制** - 用户可以自由选择日志输出方式
3. ✅ **库专属标识** - 所有日志都带有 `library="wecom_notifier"` 标识
4. ✅ **提供便捷工具** - 为新手用户提供快速配置函数

---

## 日志配置方式

### 方式 1：使用库提供的快速配置（推荐新手）

适用场景：快速上手、简单应用、不需要复杂日志管理

```python
from wecom_notifier import WeComNotifier, setup_logger

# 最简配置：输出到控制台
setup_logger(log_level="INFO")

notifier = WeComNotifier()
notifier.send_text(webhook_url=WEBHOOK_URL, content="测试消息")
```

#### 高级配置选项

```python
from wecom_notifier import setup_logger

setup_logger(
    log_level="DEBUG",           # 日志级别：DEBUG/INFO/WARNING/ERROR
    add_console=True,            # 是否输出到控制台
    console_format=None,         # 控制台格式（None 使用默认）
    add_file=True,               # 是否输出到文件
    log_file="wecom.log",        # 日志文件路径
    file_format=None,            # 文件格式（None 使用默认）
    colorize=True                # 控制台是否启用颜色
)
```

#### 自定义日志格式

```python
from wecom_notifier import setup_logger

# 自定义控制台格式（简洁版）
setup_logger(
    log_level="INFO",
    console_format="{time:HH:mm:ss} | {level} | {message}"
)

# 自定义文件格式（详细版）
setup_logger(
    log_level="DEBUG",
    add_file=True,
    log_file="wecom.log",
    file_format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}"
)
```

---

### 方式 2：在应用层统一配置（推荐生产环境）

适用场景：
- 应用已有日志系统
- 需要统一管理多个库的日志
- 需要精细的日志控制

```python
from loguru import logger
from wecom_notifier import WeComNotifier

# 配置应用的全局日志
logger.add(
    "app.log",
    level="INFO",
    rotation="10 MB",        # 日志轮转
    retention="7 days",      # 保留7天
    compression="zip",       # 压缩旧日志
    encoding="utf-8"
)

# wecom-notifier 会自动使用这个配置
notifier = WeComNotifier()
```

#### 只记录本库的日志

```python
from loguru import logger

# 使用 filter 只记录 wecom-notifier 的日志
logger.add(
    "wecom.log",
    level="DEBUG",
    filter=lambda record: record["extra"].get("library") == "wecom_notifier"
)
```

#### 分离不同来源的日志

```python
from loguru import logger

# 应用日志
logger.add(
    "app.log",
    level="INFO",
    filter=lambda record: record["extra"].get("library") != "wecom_notifier"
)

# wecom-notifier 日志
logger.add(
    "wecom.log",
    level="DEBUG",
    filter=lambda record: record["extra"].get("library") == "wecom_notifier"
)
```

---

### 方式 3：完全静默（不输出日志）

适用场景：
- 生产环境不需要库日志
- 性能敏感场景
- 只关心发送结果

```python
from wecom_notifier import WeComNotifier, disable_logger

# 禁用本库所有日志
disable_logger()

notifier = WeComNotifier()
result = notifier.send_text(webhook_url=WEBHOOK_URL, content="测试")

# 只通过返回值判断成功失败
if result.is_success():
    print("发送成功")
else:
    print(f"发送失败: {result.error}")
```

---

## 动态调整日志

### 禁用和启用

```python
from wecom_notifier import disable_logger, enable_logger

# 临时禁用（如性能测试期间）
disable_logger()
# ... 执行任务 ...

# 重新启用
enable_logger()
```

### 运行时修改日志级别

#### 方法 1：通过环境变量（推荐）

```bash
# Linux/Mac
export LOGURU_LEVEL=DEBUG
python your_app.py

# Windows
set LOGURU_LEVEL=DEBUG
python your_app.py
```

```python
import os
os.environ["LOGURU_LEVEL"] = "DEBUG"  # 在代码中设置

from wecom_notifier import WeComNotifier
notifier = WeComNotifier()
```

#### 方法 2：重新配置 handler

```python
from loguru import logger
import sys

# 移除所有现有 handler
logger.remove()

# 添加新的 handler（只显示 WARNING 及以上）
logger.add(sys.stdout, level="WARNING")
```

---

## 日志级别说明

| 级别    | 用途                       | 示例场景                        |
|---------|---------------------------|--------------------------------|
| DEBUG   | 详细的调试信息             | 开发调试、排查复杂问题          |
| INFO    | 关键操作信息（默认）       | 消息发送、队列状态、初始化      |
| WARNING | 警告但不影响功能           | 频控触发、重试、内容审核拦截    |
| ERROR   | 错误但可恢复               | 网络错误、发送失败              |

### 各级别输出示例

```python
from wecom_notifier import setup_logger, WeComNotifier

# DEBUG 级别（非常详细）
setup_logger(log_level="DEBUG")
# 输出：初始化、分段详情、频控等待、HTTP请求等
# 适用场景：开发调试

# INFO 级别（默认，推荐）
setup_logger(log_level="INFO")
# 输出：消息发送成功/失败、初始化、重要状态变化
# 适用场景：生产环境常规日志

# WARNING 级别（只显示警告和错误）
setup_logger(log_level="WARNING")
# 输出：频控触发、重试、内容审核、错误
# 适用场景：生产环境，减少日志量

# ERROR 级别（只显示错误）
setup_logger(log_level="ERROR")
# 输出：发送失败、初始化失败等
# 适用场景：只关心错误
```

---

## 与标准 logging 模块集成

如果你的应用使用 Python 标准的 `logging` 模块：

```python
import logging
from loguru import logger

# 配置 loguru 将日志转发到 logging
class PropagateHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)

logger.add(PropagateHandler(), format="{message}")

# 现在 wecom-notifier 的日志会进入标准 logging 系统
from wecom_notifier import WeComNotifier
notifier = WeComNotifier()
```

---

## 常见场景示例

### 场景 1：Flask/Django 应用

```python
# app.py
from loguru import logger
from wecom_notifier import WeComNotifier

# 应用启动时配置日志
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",  # 每天轮转
    retention="30 days",
    encoding="utf-8"
)

# 创建全局 notifier
notifier = WeComNotifier()

# 使用
@app.route("/send")
def send_notification():
    result = notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content="用户注册通知"
    )
    return {"success": result.is_success()}
```

### 场景 2：数据处理脚本

```python
from wecom_notifier import WeComNotifier, setup_logger

# 输出到控制台和文件
setup_logger(
    log_level="INFO",
    add_console=True,
    add_file=True,
    log_file="data_process.log"
)

notifier = WeComNotifier()

# 处理数据并发送通知
for data in process_large_dataset():
    # ... 处理逻辑 ...
    notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content=f"处理完成：{data['name']}"
    )
```

### 场景 3：定时任务（Cron/Celery）

```python
from wecom_notifier import WeComNotifier, setup_logger

# 只记录到文件，不输出到控制台
setup_logger(
    log_level="INFO",
    add_console=False,
    add_file=True,
    log_file="/var/log/cronjob.log"
)

notifier = WeComNotifier()

def daily_report():
    # ... 生成报告 ...
    result = notifier.send_markdown(
        webhook_url=WEBHOOK_URL,
        content=report_content
    )

    if not result.is_success():
        # 任务失败时输出到标准错误
        import sys
        print(f"ERROR: {result.error}", file=sys.stderr)
```

### 场景 4：多环境配置

```python
import os
from wecom_notifier import WeComNotifier, setup_logger, disable_logger

ENV = os.getenv("ENV", "development")

if ENV == "production":
    # 生产环境：只记录 WARNING+
    setup_logger(
        log_level="WARNING",
        add_file=True,
        log_file="/var/log/wecom.log"
    )
elif ENV == "development":
    # 开发环境：详细日志
    setup_logger(log_level="DEBUG")
elif ENV == "test":
    # 测试环境：完全静默
    disable_logger()

notifier = WeComNotifier()
```

---

## 故障排查

### 问题 1：没有看到任何日志输出

**原因**：v0.2.0+ 默认不配置日志

**解决**：
```python
from wecom_notifier import setup_logger

# 显式配置日志
setup_logger(log_level="INFO")
```

### 问题 2：日志格式不符合预期

**原因**：应用已经配置了 loguru 的全局格式

**解决**：
```python
from loguru import logger

# 移除现有配置，重新添加
logger.remove()
logger.add(sys.stdout, format="你想要的格式")
```

### 问题 3：日志文件权限错误

**原因**：日志文件路径不可写

**解决**：
```python
import os

# 确保日志目录存在且可写
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

setup_logger(
    add_file=True,
    log_file=os.path.join(log_dir, "wecom.log")
)
```

### 问题 4：看到了其他库的日志

**原因**：配置了全局 loguru，影响了所有使用 loguru 的库

**解决**：使用 filter 只保留需要的日志
```python
from loguru import logger

logger.add(
    "app.log",
    filter=lambda record: record["extra"].get("library") in ["wecom_notifier", "my_app"]
)
```

---

## 性能考虑

### 日志对性能的影响

1. **DEBUG 级别**：会记录大量信息，有一定性能开销
2. **INFO 级别**：推荐使用，性能影响可忽略
3. **WARNING+ 级别**：几乎无性能影响
4. **完全禁用**：零性能开销

### 高性能场景建议

```python
from wecom_notifier import WeComNotifier, disable_logger

# 性能敏感场景：完全禁用日志
disable_logger()

notifier = WeComNotifier()

# 通过返回值处理结果
result = notifier.send_text(webhook_url=WEBHOOK_URL, content="消息")
if not result.is_success():
    # 只在失败时记录
    your_logger.error(f"发送失败: {result.error}")
```

---

## 总结

### 最佳实践

1. **生产环境**：使用 INFO 或 WARNING 级别
2. **开发环境**：使用 DEBUG 级别
3. **统一管理**：在应用入口统一配置日志
4. **分离关注**：使用 filter 分离不同来源的日志
5. **及时轮转**：配置日志轮转避免文件过大

### 选择指南

| 场景                 | 推荐方式              | 配置示例                      |
|---------------------|----------------------|------------------------------|
| 新手快速上手         | 方式1：setup_logger  | `setup_logger("INFO")`       |
| 已有日志系统         | 方式2：应用层配置    | `logger.add("app.log")`      |
| 生产环境不需要日志   | 方式3：完全静默       | `disable_logger()`           |
| 开发调试             | 方式1：DEBUG级别      | `setup_logger("DEBUG")`      |
| 多环境部署           | 结合环境变量         | `os.getenv("LOG_LEVEL")`     |

---

## 相关资源

- [Loguru 官方文档](https://loguru.readthedocs.io/)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [wecom-notifier README](../README.md)
- [日志最佳实践](./wecom_notifier_logging_best_practices.md)
