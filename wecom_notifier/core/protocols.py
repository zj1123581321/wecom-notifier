"""
统一协议定义 - 平台无关的抽象接口

定义了发送器、频率控制器、消息转换器的标准协议，
所有平台实现必须遵循这些协议以确保互操作性。
"""
from typing import Protocol, Tuple, Optional, Any, runtime_checkable


@runtime_checkable
class SenderProtocol(Protocol):
    """
    发送器协议 - 所有平台的 Sender 必须实现

    定义统一的消息发送接口，平台实现者需要：
    1. 实现 send 方法
    2. 处理平台特定的消息格式转换
    3. 返回统一的结果格式
    """

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
            webhook_url: Webhook地址
            msg_type: 消息类型（平台自定义，如 "text", "markdown"）
            content: 消息内容（类型取决于 msg_type）
            metadata: 平台特定元数据（如 mentioned_list 等）

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
                - (True, None) 表示成功
                - (False, "error message") 表示失败
        """
        ...


@runtime_checkable
class RateLimiterProtocol(Protocol):
    """
    频率控制器协议 - 支持单层/双层频控

    定义统一的频率控制接口，用于限制发送速率。
    实现者需要保证线程安全。
    """

    def acquire(self) -> None:
        """
        获取发送许可（阻塞）

        如果当前没有可用配额，将阻塞等待直到有配额可用。
        调用此方法后会消耗一个配额。
        """
        ...

    def get_available_count(self) -> int:
        """
        返回当前可用配额

        Returns:
            int: 当前可立即使用的配额数量
        """
        ...

    def is_available_now(self) -> bool:
        """
        当前是否有配额

        Returns:
            bool: True 表示有配额可用，False 表示需要等待
        """
        ...


@runtime_checkable
class MessageConverterProtocol(Protocol):
    """
    消息转换器协议 - 将通用 Message 转换为平台格式

    用于将核心的 Message 对象转换为特定平台所需的格式。
    每个平台应实现自己的转换器。
    """

    def prepare_send_params(
        self,
        msg_type: str,
        content: Any,
        message_metadata: dict
    ) -> Tuple[str, Any, dict]:
        """
        准备发送参数

        将通用的消息参数转换为平台特定的格式。

        Args:
            msg_type: 通用消息类型
            content: 消息内容
            message_metadata: 消息元数据（如 mention_all, mentioned_list 等）

        Returns:
            Tuple[str, Any, dict]: (平台 msg_type, 平台 content, 平台 metadata)
        """
        ...


__all__ = [
    "SenderProtocol",
    "RateLimiterProtocol",
    "MessageConverterProtocol",
]
