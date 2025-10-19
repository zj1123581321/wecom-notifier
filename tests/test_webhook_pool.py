"""
测试Webhook池功能
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from wecom_notifier import WeComNotifier
from wecom_notifier.webhook_pool import WebhookPool, AllWebhooksUnavailableError
from wecom_notifier.webhook_resource import WebhookResource
from wecom_notifier.rate_limiter import RateLimiter


class TestWebhookPool:
    """测试Webhook池基础功能"""

    def test_single_webhook_backward_compatibility(self):
        """测试单webhook模式向后兼容"""
        notifier = WeComNotifier()

        # Mock sender
        with patch.object(notifier.sender, 'send_text', return_value=(True, None)):
            result = notifier.send_text(
                webhook_url="https://example.com/webhook1",
                content="Test message",
                async_send=False
            )

            assert result.is_success()
            assert len(result.used_webhooks) == 0  # 单webhook模式不填充此字段

    def test_multi_webhook_basic(self):
        """测试多webhook基础功能"""
        notifier = WeComNotifier()

        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2",
            "https://example.com/webhook3"
        ]

        # Mock sender
        with patch.object(notifier.sender, 'send_text', return_value=(True, None)):
            result = notifier.send_text(
                webhook_url=webhook_urls,
                content="Test message",
                async_send=False
            )

            assert result.is_success()
            assert len(result.used_webhooks) > 0

    def test_webhook_url_list_empty(self):
        """测试空webhook列表抛出异常"""
        notifier = WeComNotifier()

        with pytest.raises(Exception):  # InvalidParameterError
            notifier.send_text(
                webhook_url=[],
                content="Test message"
            )

    def test_webhook_url_invalid_type(self):
        """测试无效webhook_url类型抛出异常"""
        notifier = WeComNotifier()

        with pytest.raises(Exception):  # InvalidParameterError
            notifier.send_text(
                webhook_url=123,  # 错误类型
                content="Test message"
            )

    def test_pool_key_generation(self):
        """测试池key生成（顺序无关）"""
        notifier = WeComNotifier()

        urls1 = ["url1", "url2", "url3"]
        urls2 = ["url3", "url1", "url2"]  # 不同顺序

        key1 = notifier._make_pool_key(urls1)
        key2 = notifier._make_pool_key(urls2)

        assert key1 == key2  # 应该生成相同的key

    def test_rate_limiter_sharing(self):
        """测试全局RateLimiter共享"""
        notifier = WeComNotifier()

        url = "https://example.com/webhook1"

        # 单webhook模式
        with patch.object(notifier.sender, 'send_text', return_value=(True, None)):
            notifier.send_text(webhook_url=url, content="Test1", async_send=False)

        # 获取RateLimiter
        rate_limiter1 = notifier.rate_limiters.get(url)
        assert rate_limiter1 is not None

        # 多webhook模式（包含同一个URL）
        with patch.object(notifier.sender, 'send_text', return_value=(True, None)):
            notifier.send_text(
                webhook_url=[url, "https://example.com/webhook2"],
                content="Test2",
                async_send=False
            )

        # 应该使用同一个RateLimiter
        rate_limiter2 = notifier.rate_limiters.get(url)
        assert rate_limiter1 is rate_limiter2


class TestWebhookResource:
    """测试WebhookResource类"""

    def test_resource_availability(self):
        """测试资源可用性判断"""
        rate_limiter = RateLimiter()
        resource = WebhookResource("https://example.com", rate_limiter)

        # 初始状态应该可用
        assert resource.is_available()

        # 标记失败后进入冷却期
        resource.mark_failure()
        assert not resource.is_available()

        # 冷却时间应该大于0
        assert resource.get_cooldown_remaining() > 0

    def test_resource_recovery(self):
        """测试资源自动恢复"""
        rate_limiter = RateLimiter()
        resource = WebhookResource("https://example.com", rate_limiter)

        # 设置较短的冷却时间用于测试
        resource.COOLDOWN_BASE = 0.1
        resource.COOLDOWN_MAX = 0.2

        # 标记失败
        resource.mark_failure()
        assert not resource.is_available()

        # 等待冷却期
        time.sleep(0.15)

        # 应该自动恢复
        assert resource.is_available()

    def test_resource_priority_score(self):
        """测试优先级分数计算"""
        rate_limiter = RateLimiter(max_count=20)
        resource = WebhookResource("https://example.com", rate_limiter)

        # 初始状态分数应该是满配额
        score = resource.get_priority_score()
        assert score == 20

        # 获取一些配额
        rate_limiter.acquire()
        rate_limiter.acquire()

        # 分数应该减少
        new_score = resource.get_priority_score()
        assert new_score == 18

    def test_resource_consecutive_failures(self):
        """测试连续失败的冷却递增"""
        rate_limiter = RateLimiter()
        resource = WebhookResource("https://example.com", rate_limiter)

        resource.COOLDOWN_BASE = 1
        resource.COOLDOWN_MAX = 10

        # 第一次失败
        resource.mark_failure()
        cooldown1 = resource._calculate_cooldown()

        # 第二次失败
        resource.mark_failure()
        cooldown2 = resource._calculate_cooldown()

        # 冷却时间应该递增
        assert cooldown2 > cooldown1

        # 成功后应该重置
        resource.mark_success()
        assert resource.consecutive_failures == 0


class TestRateLimiterExtensions:
    """测试RateLimiter新增方法"""

    def test_get_next_available_time(self):
        """测试获取下次可用时间"""
        limiter = RateLimiter(max_count=2, time_window=60)

        # 初始状态应该立即可用
        next_time = limiter.get_next_available_time()
        assert next_time <= time.time()

        # 占用配额
        limiter.acquire()
        limiter.acquire()

        # 下次可用时间应该在未来
        next_time = limiter.get_next_available_time()
        assert next_time > time.time()

    def test_is_available_now(self):
        """测试是否立即可用"""
        limiter = RateLimiter(max_count=2, time_window=60)

        # 初始状态
        assert limiter.is_available_now()

        # 占用所有配额
        limiter.acquire()
        limiter.acquire()

        # 应该不可用
        assert not limiter.is_available_now()


class TestWebhookPoolIntegration:
    """测试Webhook池集成功能"""

    @patch('wecom_notifier.sender.Sender.send_text')
    def test_pool_load_balancing(self, mock_send):
        """测试负载均衡（最空闲优先）"""
        mock_send.return_value = (True, None)

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2",
            "https://example.com/webhook3"
        ]

        # 发送多条短消息
        for i in range(5):
            result = notifier.send_text(
                webhook_url=webhook_urls,
                content=f"Message {i}",
                async_send=False
            )
            assert result.is_success()

        # 验证send_text被调用
        assert mock_send.called

    @patch('wecom_notifier.sender.Sender.send_text')
    def test_pool_segment_distribution(self, mock_send):
        """测试分段在多webhook间分布"""
        mock_send.return_value = (True, None)

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2"
        ]

        # 发送超长消息（会被分段）
        long_content = "A" * 5000  # 超过4096字节

        result = notifier.send_text(
            webhook_url=webhook_urls,
            content=long_content,
            async_send=False
        )

        assert result.is_success()
        assert result.segment_count > 1  # 应该被分段

    @patch('wecom_notifier.sender.Sender.send_markdown')
    def test_pool_markdown_support(self, mock_send):
        """测试池支持Markdown消息"""
        mock_send.return_value = (True, None)

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2"
        ]

        result = notifier.send_markdown(
            webhook_url=webhook_urls,
            content="# Test\n\nMarkdown content",
            async_send=False
        )

        assert result.is_success()

    @patch('wecom_notifier.sender.Sender.send_image')
    def test_pool_image_support(self, mock_send):
        """测试池支持图片消息"""
        mock_send.return_value = (True, None)

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2"
        ]

        # Mock图片数据
        with patch('wecom_notifier.sender.Sender.prepare_image', return_value=("base64data", "md5hash")):
            result = notifier.send_image(
                webhook_url=webhook_urls,
                image_base64="fake_base64",
                async_send=False
            )

            assert result.is_success()


class TestPoolErrorHandling:
    """测试池的错误处理"""

    @patch('wecom_notifier.sender.Sender.send_text')
    def test_pool_single_webhook_failure(self, mock_send):
        """测试单个webhook失败时的自动切换"""
        # 第一个webhook失败，第二个成功
        mock_send.side_effect = [
            (False, "Error 1"),  # webhook1失败
            (True, None)         # webhook2成功
        ]

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2"
        ]

        result = notifier.send_text(
            webhook_url=webhook_urls,
            content="Test message",
            async_send=False
        )

        # 应该自动切换到webhook2并成功
        assert result.is_success()

    @patch('wecom_notifier.sender.Sender.send_text')
    def test_pool_all_webhooks_failure(self, mock_send):
        """测试所有webhook都失败"""
        mock_send.return_value = (False, "Network error")

        notifier = WeComNotifier()
        webhook_urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2"
        ]

        result = notifier.send_text(
            webhook_url=webhook_urls,
            content="Test message",
            async_send=False
        )

        # 应该失败
        assert not result.is_success()
        assert result.error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
