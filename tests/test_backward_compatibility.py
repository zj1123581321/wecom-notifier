"""
向后兼容性测试

验证 Phase 1 重构后所有旧的导入路径和API都能正常工作
"""
import pytest


class TestImportPaths:
    """测试所有旧的导入路径"""

    def test_import_wecom_notifier(self):
        """测试主模块导入"""
        from wecom_notifier import WeComNotifier
        assert WeComNotifier is not None

    def test_import_send_result(self):
        """测试 SendResult 导入"""
        from wecom_notifier import SendResult
        assert SendResult is not None

    def test_import_message(self):
        """测试 Message 导入"""
        from wecom_notifier import Message
        assert Message is not None

    def test_import_segment_info(self):
        """测试 SegmentInfo 导入"""
        from wecom_notifier import SegmentInfo
        assert SegmentInfo is not None

    def test_import_exceptions(self):
        """测试异常类导入"""
        from wecom_notifier import (
            WeComError,
            NetworkError,
            WebhookInvalidError,
            RateLimitError,
            InvalidParameterError,
        )
        assert WeComError is not None
        assert NetworkError is not None
        assert WebhookInvalidError is not None
        assert RateLimitError is not None
        assert InvalidParameterError is not None

    def test_import_new_exceptions(self):
        """测试新增的核心异常导入"""
        from wecom_notifier import (
            NotificationError,
            ConfigurationError,
            ModerationError,
        )
        assert NotificationError is not None
        assert ConfigurationError is not None
        assert ModerationError is not None

    def test_import_logger_functions(self):
        """测试日志工具导入"""
        from wecom_notifier import (
            setup_logger,
            disable_logger,
            enable_logger,
            get_logger,
        )
        assert setup_logger is not None
        assert disable_logger is not None
        assert enable_logger is not None
        assert get_logger is not None

    def test_import_core_classes(self):
        """测试核心类导入"""
        from wecom_notifier import RateLimiter, MessageSegmenter
        assert RateLimiter is not None
        assert MessageSegmenter is not None

    def test_import_from_models(self):
        """测试从 models 模块导入"""
        from wecom_notifier.models import Message, SendResult, SegmentInfo
        assert Message is not None
        assert SendResult is not None
        assert SegmentInfo is not None

    def test_import_from_constants(self):
        """测试从 constants 模块导入"""
        from wecom_notifier.constants import (
            MSG_TYPE_TEXT,
            MSG_TYPE_MARKDOWN_V2,
            MSG_TYPE_IMAGE,
            MAX_BYTES_PER_MESSAGE,
            DEFAULT_RATE_LIMIT,
            DEFAULT_TIME_WINDOW,
            ERRCODE_SUCCESS,
            ERRCODE_RATE_LIMIT,
        )
        assert MSG_TYPE_TEXT == "text"
        assert MSG_TYPE_MARKDOWN_V2 == "markdown_v2"
        assert MSG_TYPE_IMAGE == "image"
        assert MAX_BYTES_PER_MESSAGE == 3800
        assert DEFAULT_RATE_LIMIT == 20
        assert DEFAULT_TIME_WINDOW == 60
        assert ERRCODE_SUCCESS == 0
        assert ERRCODE_RATE_LIMIT == 45009

    def test_import_from_exceptions(self):
        """测试从 exceptions 模块导入"""
        from wecom_notifier.exceptions import (
            WeComError,
            NetworkError,
            WebhookInvalidError,
            RateLimitError,
            SegmentError,
            InvalidParameterError,
        )
        assert WeComError is not None
        assert NetworkError is not None
        assert WebhookInvalidError is not None
        assert RateLimitError is not None
        assert SegmentError is not None
        assert InvalidParameterError is not None

    def test_import_from_logger(self):
        """测试从 logger 模块导入"""
        from wecom_notifier.logger import (
            get_logger,
            setup_logger,
            disable_logger,
            enable_logger,
        )
        assert get_logger is not None
        assert setup_logger is not None
        assert disable_logger is not None
        assert enable_logger is not None

    def test_import_from_rate_limiter(self):
        """测试从 rate_limiter 模块导入"""
        from wecom_notifier.rate_limiter import RateLimiter
        assert RateLimiter is not None

    def test_import_from_segmenter(self):
        """测试从 segmenter 模块导入"""
        from wecom_notifier.segmenter import MessageSegmenter
        assert MessageSegmenter is not None


class TestCoreImports:
    """测试新的 core/ 模块导入"""

    def test_import_from_core(self):
        """测试从 core 模块导入"""
        from wecom_notifier.core import (
            RateLimiter,
            MessageSegmenter,
            Message,
            SendResult,
            SegmentInfo,
            get_logger,
            setup_logger,
            disable_logger,
            enable_logger,
        )
        assert RateLimiter is not None
        assert MessageSegmenter is not None
        assert Message is not None
        assert SendResult is not None
        assert SegmentInfo is not None
        assert get_logger is not None
        assert setup_logger is not None
        assert disable_logger is not None
        assert enable_logger is not None

    def test_import_from_core_exceptions(self):
        """测试从 core.exceptions 模块导入"""
        from wecom_notifier.core.exceptions import (
            NotificationError,
            NetworkError,
            ConfigurationError,
            ModerationError,
            SegmentationError,
            RateLimitError,
        )
        assert NotificationError is not None
        assert NetworkError is not None
        assert ConfigurationError is not None
        assert ModerationError is not None
        assert SegmentationError is not None
        assert RateLimitError is not None

    def test_import_from_core_constants(self):
        """测试从 core.constants 模块导入"""
        from wecom_notifier.core.constants import (
            DEFAULT_RATE_LIMIT,
            DEFAULT_TIME_WINDOW,
            MSG_TYPE_TEXT,
            MSG_TYPE_MARKDOWN,
        )
        assert DEFAULT_RATE_LIMIT == 20
        assert DEFAULT_TIME_WINDOW == 60
        assert MSG_TYPE_TEXT == "text"
        assert MSG_TYPE_MARKDOWN == "markdown"


class TestAPIBehavior:
    """测试API行为一致性"""

    def test_message_creation(self):
        """测试 Message 对象创建"""
        from wecom_notifier.models import Message
        from wecom_notifier.constants import MSG_TYPE_TEXT

        msg = Message(
            content="Hello, World!",
            msg_type=MSG_TYPE_TEXT,
            mention_all=False,
            mentioned_list=["user1"],
        )

        assert msg.content == "Hello, World!"
        assert msg.msg_type == MSG_TYPE_TEXT
        assert msg.mention_all is False
        assert msg.mentioned_list == ["user1"]
        assert msg.id is not None

    def test_message_needs_mention_all_workaround(self):
        """测试 Message.needs_mention_all_workaround()"""
        from wecom_notifier.models import Message
        from wecom_notifier.constants import MSG_TYPE_TEXT, MSG_TYPE_MARKDOWN_V2, MSG_TYPE_IMAGE

        # text 类型不需要 workaround
        msg_text = Message(content="test", msg_type=MSG_TYPE_TEXT, mention_all=True)
        assert msg_text.needs_mention_all_workaround() is False

        # markdown_v2 类型需要 workaround
        msg_md = Message(content="test", msg_type=MSG_TYPE_MARKDOWN_V2, mention_all=True)
        assert msg_md.needs_mention_all_workaround() is True

        # image 类型需要 workaround
        msg_img = Message(content="test", msg_type=MSG_TYPE_IMAGE, mention_all=True)
        assert msg_img.needs_mention_all_workaround() is True

        # mention_all=False 时不需要 workaround
        msg_no_mention = Message(content="test", msg_type=MSG_TYPE_MARKDOWN_V2, mention_all=False)
        assert msg_no_mention.needs_mention_all_workaround() is False

    def test_send_result_creation(self):
        """测试 SendResult 对象创建"""
        from wecom_notifier.models import SendResult

        result = SendResult(message_id="test-123")

        assert result.message_id == "test-123"
        assert result.success is None  # 初始状态
        assert result.error is None
        assert result.is_success() is False

    def test_send_result_mark_success(self):
        """测试 SendResult.mark_success()"""
        from wecom_notifier.models import SendResult

        result = SendResult(message_id="test-123")
        result.mark_success()

        assert result.success is True
        assert result.error is None
        assert result.is_success() is True

    def test_send_result_mark_failed(self):
        """测试 SendResult.mark_failed()"""
        from wecom_notifier.models import SendResult

        result = SendResult(message_id="test-123")
        result.mark_failed("Network error")

        assert result.success is False
        assert result.error == "Network error"
        assert result.is_success() is False

    def test_rate_limiter_creation(self):
        """测试 RateLimiter 对象创建"""
        from wecom_notifier.rate_limiter import RateLimiter

        limiter = RateLimiter(max_count=20, time_window=60)

        assert limiter.max_count == 20
        assert limiter.time_window == 60
        assert limiter.get_available_count() == 20
        assert limiter.is_available_now() is True

    def test_segmenter_creation(self):
        """测试 MessageSegmenter 对象创建"""
        from wecom_notifier.segmenter import MessageSegmenter
        from wecom_notifier.constants import MSG_TYPE_TEXT

        segmenter = MessageSegmenter(max_bytes=3800)

        # 短文本不需要分段
        segments = segmenter.segment("Hello, World!", MSG_TYPE_TEXT)
        assert len(segments) == 1
        assert segments[0].content == "Hello, World!"
        assert segments[0].is_first is True
        assert segments[0].is_last is True

    def test_logger_functions(self):
        """测试日志函数"""
        from wecom_notifier.logger import get_logger, disable_logger, enable_logger

        logger = get_logger()
        assert logger is not None

        # 测试禁用/启用
        disable_logger()
        enable_logger()

    def test_exception_hierarchy(self):
        """测试异常继承关系"""
        from wecom_notifier.exceptions import (
            NotificationError,
            WeComError,
            NetworkError,
            WebhookInvalidError,
            RateLimitError,
        )

        # WeComError 应该继承自 NotificationError
        assert issubclass(WeComError, NotificationError)

        # 其他异常应该继承自 WeComError
        assert issubclass(NetworkError, WeComError)
        assert issubclass(WebhookInvalidError, WeComError)
        assert issubclass(RateLimitError, WeComError)


class TestWeComNotifierInit:
    """测试 WeComNotifier 初始化"""

    def test_notifier_creation(self):
        """测试 WeComNotifier 对象创建"""
        from wecom_notifier import WeComNotifier

        notifier = WeComNotifier()

        assert notifier is not None
        assert notifier.sender is not None
        assert notifier.segmenter is not None

    def test_notifier_with_params(self):
        """测试带参数的 WeComNotifier 对象创建"""
        from wecom_notifier import WeComNotifier

        notifier = WeComNotifier(
            max_retries=5,
            retry_delay=3.0,
        )

        assert notifier is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
