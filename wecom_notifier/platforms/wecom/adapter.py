"""
企业微信适配器 - 包装现有 Sender 实现统一协议

此模块提供适配器，将现有的 WeComSender 包装为符合
SenderProtocol 的实现，实现新旧架构的桥接。
"""
from typing import Any, Optional, Tuple, TYPE_CHECKING

from wecom_notifier.constants import (
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN_V2,
    MSG_TYPE_IMAGE,
)

if TYPE_CHECKING:
    from wecom_notifier.sender import Sender


class WeComSenderAdapter:
    """
    企业微信发送器适配器

    包装现有的 Sender 类，实现 SenderProtocol 接口。
    这样可以在不修改原有 Sender 代码的情况下，
    让它符合新的协议规范。

    使用示例：
        from wecom_notifier.sender import Sender
        from wecom_notifier.platforms.wecom import WeComSenderAdapter

        sender = Sender()
        adapter = WeComSenderAdapter(sender)

        # 使用统一接口发送
        success, error = adapter.send(
            webhook_url="https://...",
            msg_type="text",
            content="Hello",
            metadata={"mentioned_list": ["@all"]}
        )
    """

    def __init__(self, sender: "Sender"):
        """
        初始化适配器

        Args:
            sender: 原生的企微 Sender 实例
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

        将统一的发送请求转换为企微原生的方法调用。

        Args:
            webhook_url: Webhook地址
            msg_type: 消息类型（text, markdown_v2, image）
            content: 消息内容
            metadata: 平台特定元数据，支持的字段：
                - mentioned_list: @的用户列表
                - mentioned_mobile_list: @的手机号列表
                - image_md5: 图片MD5值（image类型必需）

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        metadata = metadata or {}

        if msg_type == MSG_TYPE_TEXT:
            return self._sender.send_text(
                webhook_url,
                content,
                mentioned_list=metadata.get("mentioned_list"),
                mentioned_mobile_list=metadata.get("mentioned_mobile_list"),
            )

        elif msg_type == MSG_TYPE_MARKDOWN_V2:
            return self._sender.send_markdown(webhook_url, content)

        elif msg_type == MSG_TYPE_IMAGE:
            image_md5 = metadata.get("image_md5", "")
            return self._sender.send_image(webhook_url, content, image_md5)

        else:
            return False, f"Unsupported message type: {msg_type}"

    @property
    def sender(self) -> "Sender":
        """获取内部的原生 Sender 实例"""
        return self._sender


class WeComMessageConverter:
    """
    企业微信消息转换器

    实现 MessageConverterProtocol，将通用 Message 转换为企微格式。
    """

    def prepare_send_params(
        self,
        msg_type: str,
        content: Any,
        message_metadata: dict
    ) -> Tuple[str, Any, dict]:
        """
        准备发送参数

        将通用的消息参数转换为企微平台特定的格式。

        Args:
            msg_type: 通用消息类型
            content: 消息内容
            message_metadata: 消息元数据

        Returns:
            Tuple[str, Any, dict]: (企微 msg_type, 企微 content, 企微 metadata)
        """
        # 企微的 msg_type 与通用类型相同
        wecom_msg_type = msg_type

        # 内容通常不需要转换
        wecom_content = content

        # 构建企微特定的 metadata
        wecom_metadata = {}

        # 提取 @all 相关设置
        if message_metadata.get("mention_all"):
            wecom_metadata["mentioned_list"] = ["@all"]

        # 提取用户 mention 列表
        mentioned_list = message_metadata.get("mentioned_list")
        if mentioned_list:
            if "mentioned_list" in wecom_metadata:
                # 合并 @all 和其他用户
                wecom_metadata["mentioned_list"].extend(mentioned_list)
            else:
                wecom_metadata["mentioned_list"] = mentioned_list

        # 提取手机号 mention 列表
        mentioned_mobile_list = message_metadata.get("mentioned_mobile_list")
        if mentioned_mobile_list:
            wecom_metadata["mentioned_mobile_list"] = mentioned_mobile_list

        # 提取图片 MD5（如果是图片类型）
        if msg_type == MSG_TYPE_IMAGE:
            image_md5 = message_metadata.get("image_md5")
            if image_md5:
                wecom_metadata["image_md5"] = image_md5

        return wecom_msg_type, wecom_content, wecom_metadata


__all__ = [
    "WeComSenderAdapter",
    "WeComMessageConverter",
]
