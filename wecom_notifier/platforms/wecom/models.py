"""
企业微信消息模型
"""
import uuid
from typing import Optional, List, Any

from .constants import (
    MSG_TYPE_MARKDOWN_V2,
    MSG_TYPE_IMAGE,
    DEFAULT_SEGMENT_INTERVAL
)


class Message:
    """
    企业微信消息对象
    """

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


__all__ = ["Message"]
