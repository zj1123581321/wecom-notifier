"""
数据模型
"""
import threading
import uuid
from typing import Optional, List, Any, Dict
from .constants import (
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN_V2,
    MSG_TYPE_IMAGE,
    DEFAULT_SEGMENT_INTERVAL
)


class Message:
    """消息对象"""

    def __init__(
            self,
            content: Any,
            msg_type: str,
            mention_all: bool = False,
            mentioned_list: Optional[List[str]] = None,
            mentioned_mobile_list: Optional[List[str]] = None,
            segment_interval: int = DEFAULT_SEGMENT_INTERVAL,
            **kwargs
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.msg_type = msg_type
        self.mention_all = mention_all
        self.mentioned_list = mentioned_list or []
        self.mentioned_mobile_list = mentioned_mobile_list or []
        self.segment_interval = segment_interval
        self.extra_params = kwargs

    def needs_mention_all_workaround(self) -> bool:
        """是否需要额外发送@all消息（针对markdown_v2和image）"""
        return self.mention_all and self.msg_type in [MSG_TYPE_MARKDOWN_V2, MSG_TYPE_IMAGE]


class SendResult:
    """发送结果对象"""

    def __init__(self, message_id: str):
        self.message_id = message_id
        self.success: Optional[bool] = None  # None=进行中, True=成功, False=失败
        self.error: Optional[str] = None
        self._event = threading.Event()

        # 池模式的额外信息（可选）
        self.used_webhooks: List[str] = []  # 实际使用的webhook URL列表
        self.segment_count: int = 0         # 分段数量

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        等待发送完成

        Args:
            timeout: 超时时间（秒），None表示无限等待

        Returns:
            bool: 是否在超时前完成
        """
        return self._event.wait(timeout)

    def is_success(self) -> bool:
        """是否发送成功"""
        return self.success is True

    def mark_success(self):
        """标记为成功"""
        self.success = True
        self.error = None
        self._event.set()

    def mark_failed(self, error: str):
        """标记为失败"""
        self.success = False
        self.error = error
        self._event.set()

    def __repr__(self):
        status = "pending" if self.success is None else ("success" if self.success else "failed")
        return f"<SendResult message_id={self.message_id} status={status} error={self.error}>"


class SegmentInfo:
    """分段信息"""

    def __init__(
        self,
        content: str,
        is_first: bool = False,
        is_last: bool = False,
        page_number: Optional[int] = None,
        total_pages: Optional[int] = None
    ):
        self.content = content
        self.is_first = is_first
        self.is_last = is_last
        self.page_number = page_number  # 当前页码（从1开始），None表示不分页
        self.total_pages = total_pages  # 总页数，None表示不分页

    def __repr__(self):
        flags = []
        if self.is_first:
            flags.append("first")
        if self.is_last:
            flags.append("last")
        flag_str = f" ({','.join(flags)})" if flags else ""

        # 添加页码信息
        page_info = ""
        if self.page_number is not None and self.total_pages is not None:
            page_info = f" page={self.page_number}/{self.total_pages}"

        return f"<SegmentInfo length={len(self.content)}{flag_str}{page_info}>"
