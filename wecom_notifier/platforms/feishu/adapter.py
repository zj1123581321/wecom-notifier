"""
飞书平台适配器

实现 SenderProtocol 和 MessageConverterProtocol，
将飞书原生发送器包装为符合协议的实现。
"""
from typing import Any, Optional, Tuple, List, TYPE_CHECKING

from .constants import (
    MSG_TYPE_TEXT,
    MSG_TYPE_INTERACTIVE,
    DEFAULT_CARD_TEMPLATE,
)

if TYPE_CHECKING:
    from .sender import FeishuSender


class FeishuSenderAdapter:
    """
    飞书发送器适配器

    包装 FeishuSender，实现 SenderProtocol 接口。
    """

    def __init__(self, sender: "FeishuSender"):
        """
        初始化适配器

        Args:
            sender: 原生的飞书 Sender 实例
        """
        self._sender = sender

    def send(
        self,
        webhook_url: str,
        msg_type: str,
        content: Any,
        metadata: Optional[dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        统一发送接口

        Args:
            webhook_url: Webhook 地址
            msg_type: 消息类型（text, interactive）
            content: 消息内容
            metadata: 平台特定元数据：
                - title: 卡片标题（interactive 类型）
                - template: 卡片模板颜色（interactive 类型）

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        metadata = metadata or {}

        if msg_type == MSG_TYPE_TEXT:
            return self._sender.send_text(webhook_url, content)

        elif msg_type == MSG_TYPE_INTERACTIVE:
            return self._sender.send_card(
                webhook_url=webhook_url,
                content=content,
                title=metadata.get("title", "通知"),
                template=metadata.get("template", DEFAULT_CARD_TEMPLATE)
            )

        else:
            return False, f"Unsupported message type: {msg_type}"

    @property
    def sender(self) -> "FeishuSender":
        """获取内部的原生 Sender 实例"""
        return self._sender


class FeishuMessageConverter:
    """
    飞书消息转换器

    实现 MessageConverterProtocol，将通用 Message 转换为飞书格式。
    """

    def prepare_send_params(
        self,
        msg_type: str,
        content: Any,
        message_metadata: dict
    ) -> Tuple[str, Any, dict]:
        """
        准备发送参数

        Args:
            msg_type: 通用消息类型
            content: 消息内容
            message_metadata: 消息元数据

        Returns:
            Tuple[str, Any, dict]: (飞书 msg_type, 飞书 content, 飞书 metadata)
        """
        feishu_extras = message_metadata.get("feishu", {})
        feishu_metadata = {}

        # 处理 @ 功能
        if msg_type == MSG_TYPE_TEXT:
            content = self._process_mentions(content, message_metadata, feishu_extras)

        # 卡片消息元数据
        if msg_type == MSG_TYPE_INTERACTIVE:
            feishu_metadata["title"] = feishu_extras.get("title", "通知")
            feishu_metadata["template"] = feishu_extras.get(
                "template", DEFAULT_CARD_TEMPLATE
            )

        return msg_type, content, feishu_metadata

    def _process_mentions(
        self,
        content: str,
        message_metadata: dict,
        feishu_extras: dict
    ) -> str:
        """
        处理 @ 功能

        飞书的 @ 功能需要在文本中插入 <at> 标签。

        Args:
            content: 原始内容
            message_metadata: 通用元数据
            feishu_extras: 飞书特定元数据

        Returns:
            str: 处理后的内容
        """
        at_tags = []

        # 处理 mention_all
        if message_metadata.get("mention_all"):
            at_tags.append("<at user_id=\"all\">所有人</at>")

        # 处理 mentions 列表（飞书特定）
        mentions = feishu_extras.get("mentions", [])
        for user_id in mentions:
            if user_id == "all":
                if "<at user_id=\"all\">" not in " ".join(at_tags):
                    at_tags.append("<at user_id=\"all\">所有人</at>")
            else:
                at_tags.append(f"<at user_id=\"{user_id}\"></at>")

        if at_tags:
            return " ".join(at_tags) + " " + content

        return content

    @staticmethod
    def convert_markdown_to_card(
        content: str,
        title: str = "通知",
        template: str = DEFAULT_CARD_TEMPLATE
    ) -> dict:
        """
        将 Markdown 内容转换为飞书卡片结构

        Args:
            content: Markdown 内容
            title: 卡片标题
            template: 卡片模板颜色

        Returns:
            dict: 飞书卡片结构
        """
        return {
            "schema": "2.0",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": template
            },
            "body": {
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        }


__all__ = [
    "FeishuSenderAdapter",
    "FeishuMessageConverter",
]
