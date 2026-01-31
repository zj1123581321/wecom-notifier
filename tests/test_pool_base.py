"""
Webhook 池基类测试

验证 Phase 3 的 WebhookPoolBase 和 WeComWebhookPool 实现
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestPoolBaseImports:
    """测试池基类导入"""

    def test_import_webhook_pool_base(self):
        """测试 WebhookPoolBase 导入"""
        from wecom_notifier.core.pool_base import WebhookPoolBase
        assert WebhookPoolBase is not None

    def test_import_all_webhooks_unavailable_error(self):
        """测试 AllWebhooksUnavailableError 导入"""
        from wecom_notifier.core.pool_base import AllWebhooksUnavailableError
        assert AllWebhooksUnavailableError is not None

    def test_import_from_core(self):
        """测试从 core 模块导入"""
        from wecom_notifier.core import WebhookPoolBase, AllWebhooksUnavailableError
        assert WebhookPoolBase is not None
        assert AllWebhooksUnavailableError is not None


class TestWeComWebhookPoolImports:
    """测试企微池导入"""

    def test_import_from_platforms_wecom(self):
        """测试从 platforms.wecom 导入"""
        from wecom_notifier.platforms.wecom import WeComWebhookPool
        assert WeComWebhookPool is not None

    def test_import_pool_directly(self):
        """测试直接导入 pool 模块"""
        from wecom_notifier.platforms.wecom.pool import WeComWebhookPool
        assert WeComWebhookPool is not None


class TestBackwardCompatibleWebhookPool:
    """测试向后兼容的 WebhookPool"""

    def test_import_webhook_pool(self):
        """测试 WebhookPool 导入"""
        from wecom_notifier.webhook_pool import WebhookPool
        assert WebhookPool is not None

    def test_import_all_webhooks_unavailable_error_from_webhook_pool(self):
        """测试从 webhook_pool 导入 AllWebhooksUnavailableError"""
        from wecom_notifier.webhook_pool import AllWebhooksUnavailableError
        assert AllWebhooksUnavailableError is not None

    def test_webhook_pool_inherits_wecom_pool(self):
        """测试 WebhookPool 继承 WeComWebhookPool"""
        from wecom_notifier.webhook_pool import WebhookPool
        from wecom_notifier.platforms.wecom.pool import WeComWebhookPool

        assert issubclass(WebhookPool, WeComWebhookPool)


class TestWeComWebhookPoolBehavior:
    """测试 WeComWebhookPool 行为"""

    def test_should_skip_segmentation_for_image(self):
        """测试图片消息跳过分段"""
        from wecom_notifier.platforms.wecom.pool import WeComWebhookPool
        from wecom_notifier.constants import MSG_TYPE_IMAGE, MSG_TYPE_TEXT, MSG_TYPE_MARKDOWN_V2

        # 创建 mock 对象
        mock_resource = Mock()
        mock_resource.is_available.return_value = True
        mock_resource.get_priority_score.return_value = 10
        mock_resource.rate_limiter = Mock()

        mock_sender = Mock()
        mock_segmenter = Mock()

        pool = WeComWebhookPool(
            resources=[mock_resource],
            sender=mock_sender,
            segmenter=mock_segmenter,
        )

        # 图片消息应该跳过分段
        assert pool.should_skip_segmentation(MSG_TYPE_IMAGE) is True

        # 文本和 Markdown 不应跳过
        assert pool.should_skip_segmentation(MSG_TYPE_TEXT) is False
        assert pool.should_skip_segmentation(MSG_TYPE_MARKDOWN_V2) is False

        pool.stop()

    def test_should_skip_moderation_for_image(self):
        """测试图片消息跳过审核"""
        from wecom_notifier.platforms.wecom.pool import WeComWebhookPool
        from wecom_notifier.constants import MSG_TYPE_IMAGE, MSG_TYPE_TEXT, MSG_TYPE_MARKDOWN_V2

        mock_resource = Mock()
        mock_resource.is_available.return_value = True
        mock_resource.get_priority_score.return_value = 10
        mock_resource.rate_limiter = Mock()

        mock_sender = Mock()
        mock_segmenter = Mock()

        pool = WeComWebhookPool(
            resources=[mock_resource],
            sender=mock_sender,
            segmenter=mock_segmenter,
        )

        # 图片消息应该跳过审核
        assert pool.should_skip_moderation(MSG_TYPE_IMAGE) is True

        # 文本和 Markdown 不应跳过
        assert pool.should_skip_moderation(MSG_TYPE_TEXT) is False
        assert pool.should_skip_moderation(MSG_TYPE_MARKDOWN_V2) is False

        pool.stop()


class TestWebhookPoolCreation:
    """测试 WebhookPool 创建"""

    def test_pool_creation_with_mock_resources(self):
        """测试使用 mock 资源创建池"""
        from wecom_notifier.webhook_pool import WebhookPool

        mock_resource = Mock()
        mock_resource.is_available.return_value = True
        mock_resource.get_priority_score.return_value = 10
        mock_resource.rate_limiter = Mock()

        mock_sender = Mock()
        mock_segmenter = Mock()

        pool = WebhookPool(
            resources=[mock_resource],
            sender=mock_sender,
            segmenter=mock_segmenter,
        )

        assert pool is not None
        assert len(pool.resources) == 1

        pool.stop()

    def test_pool_creation_requires_resources(self):
        """测试池创建需要至少一个资源"""
        from wecom_notifier.webhook_pool import WebhookPool

        mock_sender = Mock()
        mock_segmenter = Mock()

        with pytest.raises(ValueError, match="at least one resource"):
            WebhookPool(
                resources=[],
                sender=mock_sender,
                segmenter=mock_segmenter,
            )


class TestExceptionHierarchy:
    """测试异常继承关系"""

    def test_all_webhooks_unavailable_error_inherits_notification_error(self):
        """测试 AllWebhooksUnavailableError 继承 NotificationError"""
        from wecom_notifier.core.pool_base import AllWebhooksUnavailableError
        from wecom_notifier.core.exceptions import NotificationError

        assert issubclass(AllWebhooksUnavailableError, NotificationError)

    def test_can_catch_with_notification_error(self):
        """测试可以用 NotificationError 捕获"""
        from wecom_notifier.core.pool_base import AllWebhooksUnavailableError
        from wecom_notifier.core.exceptions import NotificationError

        try:
            raise AllWebhooksUnavailableError("Test error")
        except NotificationError as e:
            assert "Test error" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
