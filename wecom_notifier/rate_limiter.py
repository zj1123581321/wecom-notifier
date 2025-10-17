"""
频率限制器 - 滑动窗口算法
"""
import threading
import time
from collections import deque
from .constants import DEFAULT_RATE_LIMIT, DEFAULT_TIME_WINDOW


class RateLimiter:
    """
    频率限制器，使用滑动窗口算法

    限制在指定时间窗口内的请求数量
    """

    def __init__(self, max_count: int = DEFAULT_RATE_LIMIT, time_window: int = DEFAULT_TIME_WINDOW):
        """
        初始化频率限制器

        Args:
            max_count: 时间窗口内的最大请求数
            time_window: 时间窗口大小（秒）
        """
        self.max_count = max_count
        self.time_window = time_window
        self.timestamps = deque()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        """
        获取一个请求配额，如果超过限制则阻塞等待

        这个方法是线程安全的
        """
        while True:
            with self.lock:
                now = time.time()

                # 清理过期的时间戳
                self._clean_expired_timestamps(now)

                # 如果还有配额，直接使用
                if len(self.timestamps) < self.max_count:
                    self.timestamps.append(now)
                    return

                # 达到限制，计算需要等待的时间
                oldest_timestamp = self.timestamps[0]
                sleep_time = self.time_window - (now - oldest_timestamp) + 0.1  # 额外加0.1秒确保安全

            # 在锁外等待（避免阻塞其他线程）
            if sleep_time > 0:
                time.sleep(sleep_time)
            # 循环重试

    def _clean_expired_timestamps(self, now: float) -> None:
        """
        清理过期的时间戳

        Args:
            now: 当前时间戳
        """
        while self.timestamps and now - self.timestamps[0] > self.time_window:
            self.timestamps.popleft()

    def get_available_count(self) -> int:
        """
        获取当前可用的请求配额数量

        Returns:
            int: 可用配额数
        """
        with self.lock:
            now = time.time()
            self._clean_expired_timestamps(now)
            return self.max_count - len(self.timestamps)

    def reset(self) -> None:
        """重置限制器"""
        with self.lock:
            self.timestamps.clear()

    def __repr__(self):
        available = self.get_available_count()
        return f"<RateLimiter max={self.max_count} window={self.time_window}s available={available}>"
