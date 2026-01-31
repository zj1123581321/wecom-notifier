"""
协议层测试

验证 Phase 2 的协议定义和适配器正确实现
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestProtocolImports:
    """测试协议导入"""

    def test_import_sender_protocol(self):
        """测试 SenderProtocol 导入"""
        from wecom_notifier.core.protocols import SenderProtocol
        assert SenderProtocol is not None

    def test_import_rate_limiter_protocol(self):
        """测试 RateLimiterProtocol 导入"""
        from wecom_notifier.core.protocols import RateLimiterProtocol
        assert RateLimiterProtocol is not None

    def test_import_message_converter_protocol(self):
        """测试 MessageConverterProtocol 导入"""
        from wecom_notifier.core.protocols import MessageConverterProtocol
        assert MessageConverterProtocol is not None

    def test_import_from_core(self):
        """测试从 core 模块导入协议"""
        from wecom_notifier.core import (
            SenderProtocol,
            RateLimiterProtocol,
            MessageConverterProtocol,
        )
        assert SenderProtocol is not None
        assert RateLimiterProtocol is not None
        assert MessageConverterProtocol is not None


class TestRateLimiterProtocol:
    """测试 RateLimiter 符合协议"""

    def test_rate_limiter_implements_protocol(self):
        """测试 RateLimiter 实现 RateLimiterProtocol"""
        from wecom_notifier.core import RateLimiter, RateLimiterProtocol

        limiter = RateLimiter()

        # 检查是否符合协议
        assert isinstance(limiter, RateLimiterProtocol)

    def test_rate_limiter_has_acquire(self):
        """测试 RateLimiter 有 acquire 方法"""
        from wecom_notifier.core import RateLimiter

        limiter = RateLimiter()
        assert hasattr(limiter, "acquire")
        assert callable(limiter.acquire)

    def test_rate_limiter_has_get_available_count(self):
        """测试 RateLimiter 有 get_available_count 方法"""
        from wecom_notifier.core import RateLimiter

        limiter = RateLimiter()
        assert hasattr(limiter, "get_available_count")
        assert callable(limiter.get_available_count)

    def test_rate_limiter_has_is_available_now(self):
        """测试 RateLimiter 有 is_available_now 方法"""
        from wecom_notifier.core import RateLimiter

        limiter = RateLimiter()
        assert hasattr(limiter, "is_available_now")
        assert callable(limiter.is_available_now)


class TestWeComAdapterImports:
    """测试企微适配器导入"""

    def test_import_from_platforms_wecom(self):
        """测试从 platforms.wecom 导入"""
        from wecom_notifier.platforms.wecom import (
            WeComSenderAdapter,
            WeComMessageConverter,
        )
        assert WeComSenderAdapter is not None
        assert WeComMessageConverter is not None

    def test_import_adapter_directly(self):
        """测试直接导入 adapter 模块"""
        from wecom_notifier.platforms.wecom.adapter import (
            WeComSenderAdapter,
            WeComMessageConverter,
        )
        assert WeComSenderAdapter is not None
        assert WeComMessageConverter is not None


class TestWeComSenderAdapter:
    """测试 WeComSenderAdapter"""

    def test_adapter_creation(self):
        """测试适配器创建"""
        from wecom_notifier.platforms.wecom import WeComSenderAdapter

        mock_sender = Mock()
        adapter = WeComSenderAdapter(mock_sender)

        assert adapter is not None
        assert adapter.sender is mock_sender

    def test_adapter_implements_sender_protocol(self):
        """测试适配器实现 SenderProtocol"""
        from wecom_notifier.core import SenderProtocol
        from wecom_notifier.platforms.wecom import WeComSenderAdapter

        mock_sender = Mock()
        adapter = WeComSenderAdapter(mock_sender)

        # 检查是否符合协议
        assert isinstance(adapter, SenderProtocol)

    def test_adapter_send_text(self):
        """测试适配器发送文本消息"""
        from wecom_notifier.platforms.wecom import WeComSenderAdapter
        from wecom_notifier.constants import MSG_TYPE_TEXT

        mock_sender = Mock()
        mock_sender.send_text.return_value = (True, None)

        adapter = WeComSenderAdapter(mock_sender)
        success, error = adapter.send(
            webhook_url="https://example.com/webhook",
            msg_type=MSG_TYPE_TEXT,
            content="Hello, World!",
            metadata={"mentioned_list": ["user1"]}
        )

        assert success is True
        assert error is None
        mock_sender.send_text.assert_called_once_with(
            "https://example.com/webhook",
            "Hello, World!",
            mentioned_list=["user1"],
            mentioned_mobile_list=None,
        )

    def test_adapter_send_markdown(self):
        """测试适配器发送 Markdown 消息"""
        from wecom_notifier.platforms.wecom import WeComSenderAdapter
        from wecom_notifier.constants import MSG_TYPE_MARKDOWN_V2

        mock_sender = Mock()
        mock_sender.send_markdown.return_value = (True, None)

        adapter = WeComSenderAdapter(mock_sender)
        success, error = adapter.send(
            webhook_url="https://example.com/webhook",
            msg_type=MSG_TYPE_MARKDOWN_V2,
            content="# Title\n\nContent",
        )

        assert success is True
        assert error is None
        mock_sender.send_markdown.assert_called_once_with(
            "https://example.com/webhook",
            "# Title\n\nContent",
        )

    def test_adapter_send_image(self):
        """测试适配器发送图片消息"""
        from wecom_notifier.platforms.wecom import WeComSenderAdapter
        from wecom_notifier.constants import MSG_TYPE_IMAGE

        mock_sender = Mock()
        mock_sender.send_image.return_value = (True, None)

        adapter = WeComSenderAdapter(mock_sender)
        success, error = adapter.send(
            webhook_url="https://example.com/webhook",
            msg_type=MSG_TYPE_IMAGE,
            content="base64_image_data",
            metadata={"image_md5": "abc123"}
        )

        assert success is True
        assert error is None
        mock_sender.send_image.assert_called_once_with(
            "https://example.com/webhook",
            "base64_image_data",
            "abc123",
        )

    def test_adapter_unsupported_type(self):
        """测试适配器处理不支持的消息类型"""
        from wecom_notifier.platforms.wecom import WeComSenderAdapter

        mock_sender = Mock()
        adapter = WeComSenderAdapter(mock_sender)

        success, error = adapter.send(
            webhook_url="https://example.com/webhook",
            msg_type="unsupported_type",
            content="content",
        )

        assert success is False
        assert "Unsupported message type" in error


class TestWeComMessageConverter:
    """测试 WeComMessageConverter"""

    def test_converter_creation(self):
        """测试转换器创建"""
        from wecom_notifier.platforms.wecom import WeComMessageConverter

        converter = WeComMessageConverter()
        assert converter is not None

    def test_converter_implements_protocol(self):
        """测试转换器实现 MessageConverterProtocol"""
        from wecom_notifier.core import MessageConverterProtocol
        from wecom_notifier.platforms.wecom import WeComMessageConverter

        converter = WeComMessageConverter()
        assert isinstance(converter, MessageConverterProtocol)

    def test_converter_prepare_text_params(self):
        """测试转换器准备文本消息参数"""
        from wecom_notifier.platforms.wecom import WeComMessageConverter
        from wecom_notifier.constants import MSG_TYPE_TEXT

        converter = WeComMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_TEXT,
            content="Hello",
            message_metadata={"mentioned_list": ["user1"]}
        )

        assert msg_type == MSG_TYPE_TEXT
        assert content == "Hello"
        assert metadata["mentioned_list"] == ["user1"]

    def test_converter_mention_all(self):
        """测试转换器处理 mention_all"""
        from wecom_notifier.platforms.wecom import WeComMessageConverter
        from wecom_notifier.constants import MSG_TYPE_TEXT

        converter = WeComMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_TEXT,
            content="Hello",
            message_metadata={"mention_all": True}
        )

        assert "@all" in metadata["mentioned_list"]

    def test_converter_merge_mentions(self):
        """测试转换器合并 mention_all 和 mentioned_list"""
        from wecom_notifier.platforms.wecom import WeComMessageConverter
        from wecom_notifier.constants import MSG_TYPE_TEXT

        converter = WeComMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_TEXT,
            content="Hello",
            message_metadata={
                "mention_all": True,
                "mentioned_list": ["user1", "user2"]
            }
        )

        assert "@all" in metadata["mentioned_list"]
        assert "user1" in metadata["mentioned_list"]
        assert "user2" in metadata["mentioned_list"]

    def test_converter_image_params(self):
        """测试转换器处理图片消息参数"""
        from wecom_notifier.platforms.wecom import WeComMessageConverter
        from wecom_notifier.constants import MSG_TYPE_IMAGE

        converter = WeComMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_IMAGE,
            content="base64_data",
            message_metadata={"image_md5": "abc123"}
        )

        assert msg_type == MSG_TYPE_IMAGE
        assert content == "base64_data"
        assert metadata["image_md5"] == "abc123"


class TestBackwardCompatibility:
    """测试向后兼容性"""

    def test_existing_sender_still_works(self):
        """测试现有 Sender 仍然可用"""
        from wecom_notifier.sender import Sender, RetryConfig

        sender = Sender()
        assert sender is not None

        # 测试带配置的创建
        config = RetryConfig(max_retries=5, retry_delay=2.0)
        sender_with_config = Sender(retry_config=config)
        assert sender_with_config is not None

    def test_existing_rate_limiter_still_works(self):
        """测试现有 RateLimiter 仍然可用"""
        from wecom_notifier.rate_limiter import RateLimiter

        limiter = RateLimiter()
        assert limiter is not None
        assert limiter.get_available_count() == 20
        assert limiter.is_available_now() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
