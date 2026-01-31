"""
飞书平台测试

验证 Phase 4 的飞书实现
"""
import pytest
from unittest.mock import Mock, patch


class TestFeishuImports:
    """测试飞书模块导入"""

    def test_import_feishu_notifier_from_main(self):
        """测试从主模块导入 FeishuNotifier"""
        from wecom_notifier import FeishuNotifier
        assert FeishuNotifier is not None

    def test_import_from_platforms_feishu(self):
        """测试从 platforms.feishu 导入"""
        from wecom_notifier.platforms.feishu import (
            FeishuNotifier,
            FeishuSender,
            FeishuSenderAdapter,
            FeishuMessageConverter,
            DualRateLimiter,
        )
        assert FeishuNotifier is not None
        assert FeishuSender is not None
        assert FeishuSenderAdapter is not None
        assert FeishuMessageConverter is not None
        assert DualRateLimiter is not None

    def test_import_exceptions(self):
        """测试导入飞书异常"""
        from wecom_notifier.platforms.feishu import (
            FeishuError,
            FeishuNetworkError,
            FeishuRateLimitError,
            FeishuKeywordError,
            FeishuIPError,
            FeishuSignError,
            FeishuBadRequestError,
        )
        assert FeishuError is not None
        assert FeishuNetworkError is not None
        assert FeishuRateLimitError is not None
        assert FeishuKeywordError is not None
        assert FeishuIPError is not None
        assert FeishuSignError is not None
        assert FeishuBadRequestError is not None

    def test_import_constants(self):
        """测试导入飞书常量"""
        from wecom_notifier.platforms.feishu.constants import (
            MSG_TYPE_TEXT,
            MSG_TYPE_INTERACTIVE,
            RATE_LIMIT_PER_MINUTE,
            RATE_LIMIT_PER_SECOND,
            CODE_SUCCESS,
            CODE_RATE_LIMIT,
        )
        assert MSG_TYPE_TEXT == "text"
        assert MSG_TYPE_INTERACTIVE == "interactive"
        assert RATE_LIMIT_PER_MINUTE == 100
        assert RATE_LIMIT_PER_SECOND == 5
        assert CODE_SUCCESS == 0
        assert CODE_RATE_LIMIT == 11232


class TestDualRateLimiter:
    """测试双层频率控制器"""

    def test_creation(self):
        """测试创建双层频率控制器"""
        from wecom_notifier.platforms.feishu import DualRateLimiter

        limiter = DualRateLimiter()
        assert limiter.minute_limit == 100
        assert limiter.second_limit == 5

    def test_custom_limits(self):
        """测试自定义限制"""
        from wecom_notifier.platforms.feishu import DualRateLimiter

        limiter = DualRateLimiter(minute_limit=50, second_limit=3)
        assert limiter.minute_limit == 50
        assert limiter.second_limit == 3

    def test_get_available_count(self):
        """测试获取可用配额"""
        from wecom_notifier.platforms.feishu import DualRateLimiter

        limiter = DualRateLimiter()
        # 初始时，秒级限制更严格（5 < 100）
        assert limiter.get_available_count() == 5

    def test_is_available_now(self):
        """测试当前是否可用"""
        from wecom_notifier.platforms.feishu import DualRateLimiter

        limiter = DualRateLimiter()
        assert limiter.is_available_now() is True

    def test_implements_protocol(self):
        """测试实现频率控制器协议"""
        from wecom_notifier.platforms.feishu import DualRateLimiter
        from wecom_notifier.core import RateLimiterProtocol

        limiter = DualRateLimiter()

        # 检查是否有协议要求的方法
        assert hasattr(limiter, "acquire")
        assert hasattr(limiter, "get_available_count")
        assert hasattr(limiter, "is_available_now")


class TestFeishuSender:
    """测试飞书发送器"""

    def test_creation(self):
        """测试创建发送器"""
        from wecom_notifier.platforms.feishu import FeishuSender

        sender = FeishuSender()
        assert sender is not None

    def test_creation_with_secret(self):
        """测试带签名密钥创建发送器"""
        from wecom_notifier.platforms.feishu import FeishuSender

        sender = FeishuSender(secret="test_secret")
        assert sender.secret == "test_secret"

    def test_gen_sign(self):
        """测试签名生成"""
        from wecom_notifier.platforms.feishu import FeishuSender

        sender = FeishuSender(secret="test_secret")
        sign = sender._gen_sign(1599360473)

        # 签名应该是 base64 编码的字符串
        assert isinstance(sign, str)
        assert len(sign) > 0


class TestFeishuSenderAdapter:
    """测试飞书发送器适配器"""

    def test_creation(self):
        """测试创建适配器"""
        from wecom_notifier.platforms.feishu import FeishuSenderAdapter

        mock_sender = Mock()
        adapter = FeishuSenderAdapter(mock_sender)
        assert adapter is not None
        assert adapter.sender is mock_sender

    def test_implements_sender_protocol(self):
        """测试实现发送器协议"""
        from wecom_notifier.core import SenderProtocol
        from wecom_notifier.platforms.feishu import FeishuSenderAdapter

        mock_sender = Mock()
        adapter = FeishuSenderAdapter(mock_sender)
        assert isinstance(adapter, SenderProtocol)

    def test_send_text(self):
        """测试发送文本消息"""
        from wecom_notifier.platforms.feishu import FeishuSenderAdapter
        from wecom_notifier.platforms.feishu.constants import MSG_TYPE_TEXT

        mock_sender = Mock()
        mock_sender.send_text.return_value = (True, None)

        adapter = FeishuSenderAdapter(mock_sender)
        success, error = adapter.send(
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
            msg_type=MSG_TYPE_TEXT,
            content="Hello, Feishu!"
        )

        assert success is True
        assert error is None
        mock_sender.send_text.assert_called_once()

    def test_send_card(self):
        """测试发送卡片消息"""
        from wecom_notifier.platforms.feishu import FeishuSenderAdapter
        from wecom_notifier.platforms.feishu.constants import MSG_TYPE_INTERACTIVE

        mock_sender = Mock()
        mock_sender.send_card.return_value = (True, None)

        adapter = FeishuSenderAdapter(mock_sender)
        success, error = adapter.send(
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
            msg_type=MSG_TYPE_INTERACTIVE,
            content="# Title\n\nContent",
            metadata={"title": "Test", "template": "blue"}
        )

        assert success is True
        assert error is None
        mock_sender.send_card.assert_called_once()


class TestFeishuMessageConverter:
    """测试飞书消息转换器"""

    def test_creation(self):
        """测试创建转换器"""
        from wecom_notifier.platforms.feishu import FeishuMessageConverter

        converter = FeishuMessageConverter()
        assert converter is not None

    def test_implements_protocol(self):
        """测试实现消息转换器协议"""
        from wecom_notifier.core import MessageConverterProtocol
        from wecom_notifier.platforms.feishu import FeishuMessageConverter

        converter = FeishuMessageConverter()
        assert isinstance(converter, MessageConverterProtocol)

    def test_prepare_text_params(self):
        """测试准备文本消息参数"""
        from wecom_notifier.platforms.feishu import FeishuMessageConverter
        from wecom_notifier.platforms.feishu.constants import MSG_TYPE_TEXT

        converter = FeishuMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_TEXT,
            content="Hello",
            message_metadata={}
        )

        assert msg_type == MSG_TYPE_TEXT
        assert content == "Hello"

    def test_process_mentions(self):
        """测试处理 @ 功能"""
        from wecom_notifier.platforms.feishu import FeishuMessageConverter
        from wecom_notifier.platforms.feishu.constants import MSG_TYPE_TEXT

        converter = FeishuMessageConverter()
        msg_type, content, metadata = converter.prepare_send_params(
            msg_type=MSG_TYPE_TEXT,
            content="Hello",
            message_metadata={"mention_all": True}
        )

        assert "<at user_id=\"all\">" in content

    def test_convert_markdown_to_card(self):
        """测试转换 Markdown 为卡片"""
        from wecom_notifier.platforms.feishu import FeishuMessageConverter

        card = FeishuMessageConverter.convert_markdown_to_card(
            content="# Title\n\nContent",
            title="Test",
            template="blue"
        )

        assert card["schema"] == "2.0"
        assert card["header"]["title"]["content"] == "Test"
        assert card["header"]["template"] == "blue"
        assert card["body"]["elements"][0]["tag"] == "markdown"


class TestFeishuNotifier:
    """测试飞书通知器"""

    def test_creation(self):
        """测试创建通知器"""
        from wecom_notifier.platforms.feishu import FeishuNotifier

        notifier = FeishuNotifier()
        assert notifier is not None

    def test_creation_with_secret(self):
        """测试带签名密钥创建通知器"""
        from wecom_notifier.platforms.feishu import FeishuNotifier

        notifier = FeishuNotifier(secret="test_secret")
        assert notifier.sender.secret == "test_secret"


class TestExceptionHierarchy:
    """测试异常继承关系"""

    def test_feishu_error_inherits_notification_error(self):
        """测试 FeishuError 继承 NotificationError"""
        from wecom_notifier.platforms.feishu import FeishuError
        from wecom_notifier.core.exceptions import NotificationError

        assert issubclass(FeishuError, NotificationError)

    def test_feishu_network_error_inherits_network_error(self):
        """测试 FeishuNetworkError 继承 NetworkError"""
        from wecom_notifier.platforms.feishu import FeishuNetworkError
        from wecom_notifier.core.exceptions import NetworkError

        assert issubclass(FeishuNetworkError, NetworkError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
