# 企业微信通知器 (WeComNotifier)

一个功能完善的企业微信机器人通知组件，专为 Python 项目设计，支持频率控制、长文本自动分段、多webhook并发管理等高级功能。

## ✨ 特性

- 🚀 **多webhook并发管理** - 每个webhook独立队列和频率控制，互不影响
- ⏱️ **智能频率控制** - 自动限制20条/分钟，符合企业微信API要求
- ✂️ **长文本自动分段** - 超过4096字节自动分段，支持Markdown语法保护
- 📝 **三种消息格式** - 支持text、markdown_v2、image
- 🎯 **@all功能增强** - 为不支持@all的格式（markdown_v2、image）自动追加text消息
- 🔄 **同步/异步模式** - 灵活选择发送模式
- 🛡️ **自动重试机制** - 网络错误和频率限制自动重试
- 📊 **详细日志记录** - 完整的调试和错误日志

## 📦 安装

### 从PyPI安装（未来发布后）

```bash
pip install wecom-notifier
```

### 从源码安装（当前）

```bash
# 克隆仓库
git clone https://github.com/yourusername/wecom-notifier.git
cd wecom-notifier

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 在其他项目中使用

```bash
# 方式1：通过相对路径安装（本地开发）
pip install -e /path/to/wecom-notifier

# 方式2：通过requirements.txt
# 在你的项目的requirements.txt中添加：
-e /path/to/wecom-notifier
```

## 🚀 快速开始

### 基础用法

```python
from wecom_notifier import WeComNotifier

# 初始化通知器
notifier = WeComNotifier()

# 发送文本消息
result = notifier.send_text(
    webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR-KEY",
    content="Hello, 企业微信！"
)

# 检查结果
if result.is_success():
    print("发送成功")
else:
    print(f"发送失败: {result.error}")
```

### 发送Markdown消息

```python
markdown_content = """# 项目部署通知

## 更新内容
- 新增用户导出功能
- 修复登录超时问题

| 测试项 | 结果 |
|--------|------|
| 单元测试 | ✅ 通过 |
| 集成测试 | ✅ 通过 |
"""

result = notifier.send_markdown(
    webhook_url=WEBHOOK_URL,
    content=markdown_content,
    mention_all=True,  # 自动追加@all
    async_send=False   # 同步等待
)
```

### 发送图片

```python
# 通过文件路径
result = notifier.send_image(
    webhook_url=WEBHOOK_URL,
    image_path="report.png",
    mention_all=True
)

# 或通过base64
result = notifier.send_image(
    webhook_url=WEBHOOK_URL,
    image_base64="your-base64-string",
    mention_all=True
)
```

### @特定用户

```python
result = notifier.send_text(
    webhook_url=WEBHOOK_URL,
    content="紧急通知！",
    mentioned_list=["user1", "user2", "@all"],  # @指定用户或所有人
    mentioned_mobile_list=["13800138000"]  # 也可以通过手机号@
)
```

## 📖 高级用法

### 并发发送

```python
notifier = WeComNotifier()

# 异步发送多条消息
results = []
for i in range(10):
    result = notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content=f"消息 {i}",
        async_send=True  # 异步发送，立即返回
    )
    results.append(result)

# 等待所有消息发送完成
for result in results:
    result.wait()  # 阻塞直到完成
    print(f"状态: {'成功' if result.is_success() else '失败'}")
```

### 多Webhook管理

```python
notifier = WeComNotifier()

webhooks = {
    "group1": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY1",
    "group2": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY2",
}

# 向不同群组发送消息（自动管理频率限制）
for name, url in webhooks.items():
    notifier.send_text(
        webhook_url=url,
        content=f"发送到 {name}"
    )
```

### 自定义配置

```python
notifier = WeComNotifier(
    max_retries=5,        # 最大重试次数
    retry_delay=3.0,      # 重试延迟（秒）
    log_level="DEBUG"     # 日志级别
)
```

### 超长文本处理

```python
# 自动分段发送
long_text = "\n".join([f"第 {i} 行" for i in range(1000)])

result = notifier.send_text(
    webhook_url=WEBHOOK_URL,
    content=long_text,
    async_send=False
)
# 会自动分段，每段不超过4096字节，并添加"续上页"/"未完待续"提示
```

### 表格智能分段

```python
# 对于超长Markdown表格，会保留表头分段
table_markdown = """
| 姓名 | 年龄 | 地址 |
|------|------|------|
""" + "\n".join([f"| 用户{i} | {20+i} | 城市{i} |" for i in range(100)])

result = notifier.send_markdown(
    webhook_url=WEBHOOK_URL,
    content=table_markdown
)
# 每个分段都会保留表头，并添加续页提示
```

## 🏗️ 架构设计

```
WeComNotifier (主类)
    ↓
WebhookManager (每个webhook一个实例)
    ↓
├── RateLimiter (频率控制：20条/分钟)
├── MessageSegmenter (智能分段)
└── Sender (HTTP发送 + 重试)
```

### 核心特性说明

#### 1. 频率控制
- 使用滑动窗口算法
- 每个webhook独立限制
- 自动阻塞等待，确保不超限

#### 2. 智能分段
- **文本**: 按行分割，尽量填满每段
- **Markdown**:
  - 保护链接、图片、代码块语法
  - 表格分段保留表头
  - 添加"续上页"/"未完待续"提示

#### 3. 消息顺序保证
- 同一消息的分段连续发送
- 不同消息按入队顺序处理
- 多webhook互不影响

#### 4. 错误处理
- 网络错误：自动重试（指数退避）
- Webhook无效：立即失败并返回错误
- 分段失败：立即停止，避免不完整消息

## 📋 API 参考

### WeComNotifier

#### 初始化参数

```python
WeComNotifier(
    max_retries=3,         # HTTP请求最大重试次数
    retry_delay=2.0,       # 重试延迟（秒）
    log_level="INFO",      # 日志级别: DEBUG/INFO/WARNING/ERROR
    logger=None            # 自定义日志记录器
)
```

#### send_text()

```python
send_text(
    webhook_url: str,                    # Webhook地址
    content: str,                        # 文本内容
    mentioned_list: List[str] = None,    # @的用户ID列表
    mentioned_mobile_list: List[str] = None,  # @的手机号列表
    async_send: bool = True              # 是否异步发送
) -> SendResult
```

#### send_markdown()

```python
send_markdown(
    webhook_url: str,      # Webhook地址
    content: str,          # Markdown内容
    mention_all: bool = False,  # 是否@所有人
    async_send: bool = True     # 是否异步发送
) -> SendResult
```

#### send_image()

```python
send_image(
    webhook_url: str,              # Webhook地址
    image_path: str = None,        # 图片文件路径
    image_base64: str = None,      # 图片base64编码（二选一）
    mention_all: bool = False,     # 是否@所有人
    async_send: bool = True        # 是否异步发送
) -> SendResult
```

### SendResult

```python
result.message_id        # 消息ID
result.is_success()      # 是否成功
result.error             # 错误信息（如果失败）
result.wait(timeout)     # 等待发送完成（异步模式）
```

## 🔍 常见问题

### Q: 如何在多个项目中共享此组件？

**A:** 有以下几种方式：

1. **本地开发模式**（推荐用于开发）：
   ```bash
   pip install -e /path/to/wecom-notifier
   ```

2. **发布到PyPI**（推荐用于生产）：
   ```bash
   # 构建
   python setup.py sdist bdist_wheel
   # 上传
   twine upload dist/*
   # 在其他项目中安装
   pip install wecom-notifier
   ```

3. **Git子模块**：
   ```bash
   git submodule add https://github.com/yourusername/wecom-notifier.git
   pip install -e ./wecom-notifier
   ```

### Q: 如何更新其他项目中的此组件？

**A:**
- 如果使用 `pip install -e`：组件代码自动同步
- 如果从PyPI安装：`pip install --upgrade wecom-notifier`
- 如果使用git子模块：`git submodule update --remote`

### Q: 消息发送顺序会乱吗？

**A:** 不会。同一消息的分段保证连续发送，不会被其他消息插入。

### Q: 如果超过20条/分钟会怎样？

**A:** 会自动等待，不会触发企业微信的限制。

### Q: 支持哪些Python版本？

**A:** Python 3.7+

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

- 项目主页: https://github.com/yourusername/wecom-notifier
- 问题反馈: https://github.com/yourusername/wecom-notifier/issues

## 🙏 致谢

感谢企业微信开放平台提供的API文档。
