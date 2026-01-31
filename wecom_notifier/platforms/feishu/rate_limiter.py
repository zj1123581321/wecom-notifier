"""
飞书双层频率控制器

飞书的频率限制：100 条/分钟 + 5 条/秒
需要同时满足两个限制条件。
"""
from wecom_notifier.core.rate_limiter import RateLimiter
from .constants import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_SECOND


class DualRateLimiter:
    """
    双层频率控制器

    飞书限制：100 条/分钟 + 5 条/秒
    两个限制都需要满足才能发送。
    """

    def __init__(
        self,
        minute_limit: int = RATE_LIMIT_PER_MINUTE,
        second_limit: int = RATE_LIMIT_PER_SECOND
    ):
        """
        初始化双层频率控制器

        Args:
            minute_limit: 每分钟最大请求数，默认 100
            second_limit: 每秒最大请求数，默认 5
        """
        self.minute_limiter = RateLimiter(max_count=minute_limit, time_window=60)
        self.second_limiter = RateLimiter(max_count=second_limit, time_window=1)

        # 保存配置
        self.minute_limit = minute_limit
        self.second_limit = second_limit

    def acquire(self) -> None:
        """
        获取发送许可（阻塞）

        同时满足分钟级和秒级限制后才返回。
        会先等待分钟级限制，再等待秒级限制。
        """
        self.minute_limiter.acquire()
        self.second_limiter.acquire()

    def get_available_count(self) -> int:
        """
        返回当前可用配额

        Returns:
            int: 两个限制中较小的可用配额
        """
        return min(
            self.minute_limiter.get_available_count(),
            self.second_limiter.get_available_count()
        )

    def is_available_now(self) -> bool:
        """
        当前是否有配额

        Returns:
            bool: 两个限制都有配额才返回 True
        """
        return (
            self.minute_limiter.is_available_now() and
            self.second_limiter.is_available_now()
        )

    def get_next_available_time(self) -> float:
        """
        获取下次有配额可用的时间戳

        Returns:
            float: 两个限制中较晚的下次可用时间
        """
        return max(
            self.minute_limiter.get_next_available_time(),
            self.second_limiter.get_next_available_time()
        )

    def reset(self) -> None:
        """重置两个限制器"""
        self.minute_limiter.reset()
        self.second_limiter.reset()

    def __repr__(self):
        minute_available = self.minute_limiter.get_available_count()
        second_available = self.second_limiter.get_available_count()
        return (
            f"<DualRateLimiter "
            f"minute={minute_available}/{self.minute_limit} "
            f"second={second_available}/{self.second_limit}>"
        )


__all__ = ["DualRateLimiter"]
