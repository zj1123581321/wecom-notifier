"""
飞书通知器使用示例

API 说明:
- FeishuNotifier(secret=None) - 创建通知器实例，可选签名密钥
- send_text(webhook_url, content, mention_all=False, mentions=None, async_send=True)
- send_card(webhook_url, content, title="通知", template="blue", async_send=True)
  - content: Markdown 格式的卡片内容
  - template: 卡片颜色模板 (blue/green/orange/red/...)
"""
from wecom_notifier import FeishuNotifier

# 替换为你的Webhook地址
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR-TOKEN-HERE"
# 如果启用了签名验证，填写签名密钥
SECRET = None  # 或 "your-secret-key"


def example_text_notification():
    """示例1：发送文本通知"""
    print("=" * 50)
    print("示例1：发送文本通知")
    print("=" * 50)

    # 创建通知器（签名密钥可选）
    notifier = FeishuNotifier(secret=SECRET)

    # 简单文本
    result = notifier.send_text(
        WEBHOOK_URL,
        "这是一条测试消息",
        async_send=False
    )

    print(f"消息ID: {result.message_id}")
    print(f"发送成功: {result.is_success()}")


def example_text_with_mention():
    """示例2：发送带@的文本"""
    print("\n" + "=" * 50)
    print("示例2：发送带@的文本")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    # @所有人
    result = notifier.send_text(
        WEBHOOK_URL,
        "紧急通知：服务器CPU使用率超过90%！",
        mention_all=True,
        async_send=False
    )
    print(f"@所有人 发送成功: {result.is_success()}")

    # @特定用户（通过 user_id）
    # 飞书的 @ 功能通过 mentions 参数传入 user_id 列表
    result = notifier.send_text(
        WEBHOOK_URL,
        "请审批这个请求",
        mentions=["ou_xxx"],  # open_id 或 user_id
        async_send=False
    )
    print(f"@用户 发送成功: {result.is_success()}")


def example_card_simple():
    """示例3：发送简单卡片消息"""
    print("\n" + "=" * 50)
    print("示例3：发送简单卡片消息")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    # 卡片内容使用 Markdown 格式
    content = """**项目名称**: 用户管理系统
**版本号**: v2.3.1
**部署时间**: 2025-01-17 10:30:00

**更新内容**:
- 新增用户导出功能
- 修复登录超时问题
- 优化数据库查询性能
"""

    result = notifier.send_card(
        WEBHOOK_URL,
        content,
        title="项目部署通知",
        template="green",  # 绿色头部
        async_send=False
    )

    if result.is_success():
        print("卡片消息发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_card_alert():
    """示例4：发送告警卡片"""
    print("\n" + "=" * 50)
    print("示例4：发送告警卡片")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    content = """**告警级别**: Critical
**服务名称**: api-gateway
**错误信息**: Connection timeout to database
**发生时间**: 2025-01-17 15:30:45

```
Traceback (most recent call last):
  File "app.py", line 45
    conn = db.connect()
TimeoutError: Connection timed out
```
"""

    result = notifier.send_card(
        WEBHOOK_URL,
        content,
        title="服务告警",
        template="red",  # 红色头部表示告警
        async_send=False
    )

    if result.is_success():
        print("告警卡片发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_card_report():
    """示例5：发送报告卡片"""
    print("\n" + "=" * 50)
    print("示例5：发送报告卡片")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    content = """**每日统计报告**

| 指标 | 数值 |
|------|------|
| API成功率 | 99.8% |
| 平均响应时间 | 120ms |
| 活跃用户数 | 12,543 |

**任务统计**:
- 完成: 15
- 进行中: 8
- 待处理: 3
"""

    result = notifier.send_card(
        WEBHOOK_URL,
        content,
        title="每日报告",
        template="blue",  # 蓝色头部
        async_send=False
    )

    if result.is_success():
        print("报告卡片发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_card_warning():
    """示例6：发送警告卡片"""
    print("\n" + "=" * 50)
    print("示例6：发送警告卡片")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    content = """**警告**: 服务器CPU使用率较高

**当前值**: 85%
**阈值**: 80%

请关注服务器状态，必要时进行扩容。
"""

    result = notifier.send_card(
        WEBHOOK_URL,
        content,
        title="性能警告",
        template="orange",  # 橙色头部表示警告
        async_send=False
    )

    if result.is_success():
        print("警告卡片发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_long_text():
    """示例7：发送超长文本（自动分段）"""
    print("\n" + "=" * 50)
    print("示例7：发送超长文本（自动分段）")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    # 生成一个超长文本
    long_text = "\n".join([f"这是第 {i} 行内容" for i in range(200)])

    result = notifier.send_text(
        WEBHOOK_URL,
        long_text,
        async_send=False
    )

    if result.is_success():
        print(f"超长文本发送成功！分段数: {result.segment_count}")
    else:
        print(f"发送失败: {result.error}")


def example_error_handling():
    """示例8：错误处理"""
    print("\n" + "=" * 50)
    print("示例8：错误处理")
    print("=" * 50)

    notifier = FeishuNotifier()

    # 使用无效的webhook
    result = notifier.send_text(
        "https://open.feishu.cn/open-apis/bot/v2/hook/invalid-token",
        "测试消息",
        async_send=False
    )

    if result.is_success():
        print("发送成功")
    else:
        print(f"发送失败，原因: {result.error}")


def example_async_send():
    """示例9：异步发送"""
    print("\n" + "=" * 50)
    print("示例9：异步发送")
    print("=" * 50)

    notifier = FeishuNotifier(secret=SECRET)

    # 异步发送多条消息
    results = []
    for i in range(3):
        result = notifier.send_text(
            WEBHOOK_URL,
            f"异步测试消息 {i + 1}",
            async_send=True  # 异步发送，立即返回
        )
        results.append(result)
        print(f"消息 {i + 1} 已加入队列")

    # 等待所有消息发送完成
    for i, result in enumerate(results):
        result.wait()
        print(f"消息 {i + 1}: {'成功' if result.is_success() else '失败'}")


if __name__ == "__main__":
    print("飞书通知器使用示例\n")

    # 运行示例（根据需要注释/取消注释）
    example_text_notification()
    # example_text_with_mention()
    # example_card_simple()
    # example_card_alert()
    # example_card_report()
    # example_card_warning()
    # example_long_text()
    # example_error_handling()
    # example_async_send()

    print("\n示例运行完成！")
