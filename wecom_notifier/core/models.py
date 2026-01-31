"""
核心数据模型 - 平台无关
"""
import threading
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict


# 核心消息类型常量
MSG_TYPE_TEXT = "text"


@dataclass
class Message:
    """
    通用消息模型

    设计原则：
    - 核心字段保持平台无关
    - 平台特定数据放在 platform_extras
    - 通过 __post_init__ 实现向后兼容
    """
    content: Any  # 消息内容（文本、图片数据等）
    msg_type: str  # 消息类型（平台自定义）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # 通用@功能
    mention_all: bool = False

    # 平台特定扩展
    platform_extras: Dict[str, Any] = field(default_factory=dict)

    # 发送配置
    segment_interval: int = 1000  # 毫秒

    # 向后兼容字段（企微）
    mentioned_list: Optional[List[str]] = None
    mentioned_mobile_list: Optional[List[str]] = None

    # 额外参数（向后兼容）
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理 - 兼容性转换"""
        # 确保 platform_extras 存在
        if self.platform_extras is None:
            self.platform_extras = {}

        # 如果设置了 mentioned_list，自动放入 platform_extras
        if self.mentioned_list or self.mentioned_mobile_list:
            if 'wecom' not in self.platform_extras:
                self.platform_extras['wecom'] = {}
            if self.mentioned_list:
                self.platform_extras['wecom']['mentioned_list'] = self.mentioned_list
            if self.mentioned_mobile_list:
                self.platform_extras['wecom']['mentioned_mobile_list'] = self.mentioned_mobile_list

    def needs_mention_all_workaround(self) -> bool:
        """
        是否需要额外发送@all消息

        默认返回 False，平台特定的实现应覆盖此方法
        """
        return False


class SendResult:
    """发送结果对象（平台无关）"""

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


@dataclass
class SegmentInfo:
    """分段信息"""
    content: str
    is_first: bool = False
    is_last: bool = False
    page_number: Optional[int] = None  # 当前页码（从1开始），None表示不分页
    total_pages: Optional[int] = None  # 总页数，None表示不分页

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
