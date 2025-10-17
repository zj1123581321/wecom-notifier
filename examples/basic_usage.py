"""
企业微信通知器使用示例
"""
from wecom_notifier import WeComNotifier

# 替换为你的Webhook地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR-KEY-HERE"


def example_text_notification():
    """示例1：发送文本通知"""
    print("=" * 50)
    print("示例1：发送文本通知")
    print("=" * 50)

    notifier = WeComNotifier()

    # 简单文本
    result = notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content="这是一条测试消息"
    )

    print(f"消息ID: {result.message_id}")
    print(f"发送成功: {result.is_success()}")


def example_text_with_mention():
    """示例2：发送带@的文本"""
    print("\n" + "=" * 50)
    print("示例2：发送带@的文本")
    print("=" * 50)

    notifier = WeComNotifier()

    result = notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content="紧急通知：服务器CPU使用率超过90%！",
        mentioned_list=["@all"]  # @所有人
    )

    print(f"发送成功: {result.is_success()}")


def example_long_text():
    """示例3：发送超长文本（自动分段）"""
    print("\n" + "=" * 50)
    print("示例3：发送超长文本（自动分段）")
    print("=" * 50)

    notifier = WeComNotifier()

    # 生成一个超长文本
    long_text = "\n".join([f"这是第 {i} 行内容" for i in range(200)])

    result = notifier.send_text(
        webhook_url=WEBHOOK_URL,
        content=long_text,
        async_send=False  # 同步发送，等待完成
    )

    if result.is_success():
        print("超长文本发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_markdown():
    """示例4：发送Markdown消息"""
    print("\n" + "=" * 50)
    print("示例4：发送Markdown消息")
    print("=" * 50)

    notifier = WeComNotifier()

    markdown_content = """# 项目部署通知

## 部署信息
- **项目名称**: 用户管理系统
- **版本号**: v2.3.1
- **部署时间**: 2025-01-17 10:30:00

## 更新内容
1. 新增用户导出功能
2. 修复登录超时问题
3. 优化数据库查询性能

## 测试结果
| 测试项 | 结果 |
|--------|------|
| 单元测试 | ✅ 通过 |
| 集成测试 | ✅ 通过 |
| 性能测试 | ✅ 通过 |

[查看详细报告](https://example.com/report)
"""

    result = notifier.send_markdown(
        webhook_url=WEBHOOK_URL,
        content=markdown_content,
        mention_all=True,  # 会额外发送一条@all消息
        async_send=False
    )

    if result.is_success():
        print("Markdown消息发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_image():
    """示例5：发送图片"""
    print("\n" + "=" * 50)
    print("示例5：发送图片")
    print("=" * 50)

    notifier = WeComNotifier()

    # 方式1：通过文件路径
    result = notifier.send_image(
        webhook_url=WEBHOOK_URL,
        image_path="path/to/your/image.jpg",
        mention_all=True
    )

    # 方式2：通过base64（如果你已经有base64数据）
    # result = notifier.send_image(
    #     webhook_url=WEBHOOK_URL,
    #     image_base64="your-base64-string-here",
    #     mention_all=True
    # )

    print(f"发送成功: {result.is_success()}")


def example_concurrent_notifications():
    """示例6：并发发送多条通知"""
    print("\n" + "=" * 50)
    print("示例6：并发发送多条通知")
    print("=" * 50)

    notifier = WeComNotifier()

    # 异步发送多条消息
    results = []
    for i in range(5):
        result = notifier.send_text(
            webhook_url=WEBHOOK_URL,
            content=f"并发测试消息 {i + 1}",
            async_send=True  # 异步发送
        )
        results.append(result)

    # 等待所有消息发送完成
    for i, result in enumerate(results):
        result.wait()
        print(f"消息 {i + 1}: {'成功' if result.is_success() else '失败'}")


def example_multiple_webhooks():
    """示例7：向多个webhook发送消息"""
    print("\n" + "=" * 50)
    print("示例7：向多个webhook发送消息")
    print("=" * 50)

    notifier = WeComNotifier()

    webhook_urls = [
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY1",
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY2",
    ]

    for url in webhook_urls:
        notifier.send_text(
            webhook_url=url,
            content="多webhook测试消息",
            async_send=True
        )

    print("已向所有webhook发送消息")


def example_error_handling():
    """示例8：错误处理"""
    print("\n" + "=" * 50)
    print("示例8：错误处理")
    print("=" * 50)

    notifier = WeComNotifier()

    # 使用无效的webhook（会失败）
    result = notifier.send_text(
        webhook_url="https://invalid-webhook-url.com",
        content="测试消息",
        async_send=False
    )

    if result.is_success():
        print("发送成功")
    else:
        print(f"发送失败，原因: {result.error}")


if __name__ == "__main__":
    print("企业微信通知器使用示例\n")

    # 运行示例（根据需要注释/取消注释）
    example_text_notification()
    # example_text_with_mention()
    # example_long_text()
    # example_markdown()
    # example_image()
    # example_concurrent_notifications()
    # example_multiple_webhooks()
    # example_error_handling()

    print("\n示例运行完成！")
