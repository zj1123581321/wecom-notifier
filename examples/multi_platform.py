"""
多平台通知示例 - 同时发送到企业微信和飞书
"""
from wecom_notifier import WeComNotifier, FeishuNotifier

# 配置
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR-KEY"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR-TOKEN"
FEISHU_SECRET = None  # 如果启用了签名验证


def notify_all(title: str, content: str, mention_all: bool = False):
    """
    向所有平台发送通知

    Args:
        title: 通知标题
        content: 通知内容（Markdown格式）
        mention_all: 是否@所有人
    """
    results = {}

    # 发送到企业微信
    wecom = WeComNotifier()
    wecom_result = wecom.send_markdown(
        webhook_url=WECOM_WEBHOOK,
        content=f"# {title}\n\n{content}",
        mention_all=mention_all,
        async_send=True
    )
    results['wecom'] = wecom_result

    # 发送到飞书
    feishu = FeishuNotifier(secret=FEISHU_SECRET)
    feishu_result = feishu.send_card(
        FEISHU_WEBHOOK,
        content,
        title=title,
        template="blue",
        async_send=True
    )
    results['feishu'] = feishu_result

    # 等待所有发送完成
    for platform, result in results.items():
        result.wait()
        status = "成功" if result.is_success() else f"失败: {result.error}"
        print(f"[{platform}] {status}")

    return results


def example_deployment_notification():
    """示例：部署通知"""
    print("=" * 50)
    print("发送部署通知到所有平台")
    print("=" * 50)

    content = """**项目**: 用户管理系统
**版本**: v2.3.1
**环境**: Production
**部署时间**: 2025-01-17 10:30:00

**更新内容**:
- 新增用户导出功能
- 修复登录超时问题
- 优化数据库查询性能

**测试结果**: 全部通过"""

    notify_all(
        title="部署完成",
        content=content,
        mention_all=False
    )


def example_alert_notification():
    """示例：告警通知"""
    print("\n" + "=" * 50)
    print("发送告警通知到所有平台")
    print("=" * 50)

    content = """**告警级别**: Critical
**服务名称**: api-gateway
**告警内容**: 服务响应时间超过阈值
**当前值**: 5.2s (阈值: 2s)
**持续时间**: 5分钟

请立即排查！"""

    notify_all(
        title="服务告警",
        content=content,
        mention_all=True  # @所有人
    )


def example_daily_report():
    """示例：日报通知"""
    print("\n" + "=" * 50)
    print("发送日报到所有平台")
    print("=" * 50)

    content = """**日期**: 2025-01-17

**任务统计**:
| 类型 | 数量 |
|------|------|
| 完成 | 15 |
| 进行中 | 8 |
| 待处理 | 3 |

**关键指标**:
- API 成功率: 99.8%
- 平均响应时间: 120ms
- 活跃用户数: 12,543"""

    notify_all(
        title="每日统计报告",
        content=content,
        mention_all=False
    )


class MultiPlatformNotifier:
    """
    多平台通知器封装类

    使用方式:
        notifier = MultiPlatformNotifier(
            wecom_url="...",
            feishu_url="...",
            feishu_secret="..."
        )
        notifier.notify("标题", "内容")
    """

    def __init__(
        self,
        wecom_url: str = None,
        feishu_url: str = None,
        feishu_secret: str = None
    ):
        self.wecom_url = wecom_url
        self.feishu_url = feishu_url

        if wecom_url:
            self.wecom = WeComNotifier()
        else:
            self.wecom = None

        if feishu_url:
            self.feishu = FeishuNotifier(secret=feishu_secret)
        else:
            self.feishu = None

    def notify(
        self,
        title: str,
        content: str,
        mention_all: bool = False,
        async_send: bool = True
    ) -> dict:
        """
        向所有配置的平台发送通知

        Args:
            title: 通知标题
            content: 通知内容（Markdown格式）
            mention_all: 是否@所有人
            async_send: 是否异步发送

        Returns:
            dict: 各平台的发送结果
        """
        results = {}

        # 企业微信
        if self.wecom and self.wecom_url:
            results['wecom'] = self.wecom.send_markdown(
                webhook_url=self.wecom_url,
                content=f"# {title}\n\n{content}",
                mention_all=mention_all,
                async_send=async_send
            )

        # 飞书
        if self.feishu and self.feishu_url:
            results['feishu'] = self.feishu.send_card(
                self.feishu_url,
                content,
                title=title,
                template="blue",
                async_send=async_send
            )

        return results


def example_class_usage():
    """示例：使用封装类"""
    print("\n" + "=" * 50)
    print("使用封装类发送通知")
    print("=" * 50)

    notifier = MultiPlatformNotifier(
        wecom_url=WECOM_WEBHOOK,
        feishu_url=FEISHU_WEBHOOK,
        feishu_secret=FEISHU_SECRET
    )

    results = notifier.notify(
        title="测试通知",
        content="这是通过封装类发送的测试消息",
        async_send=False
    )

    for platform, result in results.items():
        status = "成功" if result.is_success() else f"失败: {result.error}"
        print(f"[{platform}] {status}")


if __name__ == "__main__":
    print("多平台通知示例\n")

    # 运行示例（根据需要注释/取消注释）
    example_deployment_notification()
    # example_alert_notification()
    # example_daily_report()
    # example_class_usage()

    print("\n示例运行完成！")
