"""
飞书通知器使用示例
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

    notifier = FeishuNotifier(
        webhook_url=WEBHOOK_URL,
        secret=SECRET
    )

    # 简单文本
    result = notifier.send_text("这是一条测试消息")

    print(f"消息ID: {result.message_id}")
    print(f"发送成功: {result.is_success()}")


def example_text_with_mention():
    """示例2：发送带@的文本"""
    print("\n" + "=" * 50)
    print("示例2：发送带@的文本")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    # @所有人
    result = notifier.send_text(
        "紧急通知：服务器CPU使用率超过90%！",
        at_all=True
    )
    print(f"@所有人 发送成功: {result.is_success()}")

    # @特定用户（通过手机号）
    result = notifier.send_text(
        "请查看这个问题",
        at_mobiles=["13800138000"]
    )
    print(f"@手机号 发送成功: {result.is_success()}")

    # @特定用户（通过open_id）
    result = notifier.send_text(
        "请审批这个请求",
        at_open_ids=["ou_xxx"]
    )
    print(f"@open_id 发送成功: {result.is_success()}")


def example_rich_text():
    """示例3：发送富文本消息"""
    print("\n" + "=" * 50)
    print("示例3：发送富文本消息")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    # 富文本内容，每个列表元素是一行
    content = [
        [
            {"tag": "text", "text": "项目构建通知\n"},
        ],
        [
            {"tag": "text", "text": "状态："},
            {"tag": "text", "text": "成功", "style": ["bold"]},
        ],
        [
            {"tag": "text", "text": "详情请查看："},
            {"tag": "a", "text": "构建报告", "href": "https://example.com/build"},
        ],
    ]

    result = notifier.send_rich_text(
        title="CI/CD 通知",
        content=content
    )

    if result.is_success():
        print("富文本消息发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_card_simple():
    """示例4：发送简单卡片消息"""
    print("\n" + "=" * 50)
    print("示例4：发送简单卡片消息")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    elements = [
        {
            "tag": "div",
            "text": {
                "content": "**项目名称**: 用户管理系统\n**版本号**: v2.3.1\n**部署时间**: 2025-01-17 10:30:00",
                "tag": "lark_md"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": "此消息由自动化部署系统发送"
                }
            ]
        }
    ]

    result = notifier.send_card(
        title="项目部署通知",
        elements=elements,
        header_color="green"
    )

    if result.is_success():
        print("卡片消息发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_card_with_buttons():
    """示例5：发送带按钮的卡片消息"""
    print("\n" + "=" * 50)
    print("示例5：发送带按钮的卡片消息")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    elements = [
        {
            "tag": "div",
            "text": {
                "content": "有新的审批请求需要处理：\n\n**申请人**: 张三\n**申请类型**: 请假申请\n**申请天数**: 3天",
                "tag": "lark_md"
            }
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "同意"
                    },
                    "type": "primary",
                    "url": "https://example.com/approve"
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "拒绝"
                    },
                    "type": "danger",
                    "url": "https://example.com/reject"
                }
            ]
        }
    ]

    result = notifier.send_card(
        title="审批通知",
        elements=elements,
        header_color="orange"
    )

    if result.is_success():
        print("带按钮卡片发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_error_alert():
    """示例6：发送错误告警"""
    print("\n" + "=" * 50)
    print("示例6：发送错误告警")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    elements = [
        {
            "tag": "div",
            "text": {
                "content": "**错误级别**: Critical\n**服务名称**: api-gateway\n**错误信息**: Connection timeout to database\n**发生时间**: 2025-01-17 15:30:45",
                "tag": "lark_md"
            }
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "text": {
                "content": "```\nTraceback (most recent call last):\n  File \"app.py\", line 45\n    conn = db.connect()\nTimeoutError: Connection timed out\n```",
                "tag": "lark_md"
            }
        }
    ]

    result = notifier.send_card(
        title="服务告警",
        elements=elements,
        header_color="red"
    )

    if result.is_success():
        print("告警卡片发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_long_text():
    """示例7：发送超长文本（自动分段）"""
    print("\n" + "=" * 50)
    print("示例7：发送超长文本（自动分段）")
    print("=" * 50)

    notifier = FeishuNotifier(webhook_url=WEBHOOK_URL, secret=SECRET)

    # 生成一个超长文本
    long_text = "\n".join([f"这是第 {i} 行内容" for i in range(200)])

    result = notifier.send_text(
        long_text,
        async_send=False  # 同步发送，等待完成
    )

    if result.is_success():
        print("超长文本发送成功！")
    else:
        print(f"发送失败: {result.error}")


def example_error_handling():
    """示例8：错误处理"""
    print("\n" + "=" * 50)
    print("示例8：错误处理")
    print("=" * 50)

    # 使用无效的webhook
    notifier = FeishuNotifier(
        webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/invalid-token"
    )

    result = notifier.send_text(
        "测试消息",
        async_send=False
    )

    if result.is_success():
        print("发送成功")
    else:
        print(f"发送失败，原因: {result.error}")


if __name__ == "__main__":
    print("飞书通知器使用示例\n")

    # 运行示例（根据需要注释/取消注释）
    example_text_notification()
    # example_text_with_mention()
    # example_rich_text()
    # example_card_simple()
    # example_card_with_buttons()
    # example_error_alert()
    # example_long_text()
    # example_error_handling()

    print("\n示例运行完成！")
