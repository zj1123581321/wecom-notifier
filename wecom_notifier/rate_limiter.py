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
        self.lockout_until = 0.0  # 服务端频控锁定期（时间戳）

    def acquire(self) -> None:
        """
        获取一个请求配额，如果超过限制则阻塞等待

        这个方法是线程安全的，会考虑：
        1. 本地频率限制（滑动窗口）
        2. 服务端频控锁定期（如果服务端返回过频控错误）
        """
        while True:
            with self.lock:
                now = time.time()

                # 检查是否处于服务端频控锁定期
                if now < self.lockout_until:
                    lockout_remaining = self.lockout_until - now
                    # 在锁外等待
                else:
                    lockout_remaining = 0

            # 如果处于锁定期，先等待锁定期结束
            if lockout_remaining > 0:
                time.sleep(lockout_remaining)
                continue

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

    def get_next_available_time(self) -> float:
        """
        获取下次有配额可用的时间戳

        Returns:
            float: 下次可用的时间戳（如果当前有配额则返回当前时间）
        """
        with self.lock:
            now = time.time()
            self._clean_expired_timestamps(now)

            # 如果当前有配额，立即可用
            if len(self.timestamps) < self.max_count:
                return now

            # 否则，等最老的时间戳过期
            oldest_timestamp = self.timestamps[0]
            return oldest_timestamp + self.time_window

    def is_available_now(self) -> bool:
        """
        检查当前是否有可用配额（不考虑服务端锁定期）

        Returns:
            bool: 是否有可用配额
        """
        with self.lock:
            now = time.time()
            self._clean_expired_timestamps(now)
            return len(self.timestamps) < self.max_count

    def mark_server_rate_limited(self, lockout_duration: int = None) -> None:
        """
        标记服务端返回了频控错误，进入锁定期

        在锁定期内，所有 acquire() 调用都会等待，直到锁定期结束。
        这确保了即使其他程序触发了频控，当前程序的消息也能在等待后成功发送。

        Args:
            lockout_duration: 锁定时长（秒），默认使用时间窗口大小
        """
        if lockout_duration is None:
            lockout_duration = self.time_window

        with self.lock:
            now = time.time()
            self.lockout_until = now + lockout_duration
            # 清空本地时间戳记录，因为它们可能不准确
            # （服务端的频控可能是由其他程序触发的）
            self.timestamps.clear()

    def reset(self) -> None:
        """重置限制器"""
        with self.lock:
            self.timestamps.clear()
            self.lockout_until = 0.0

    def __repr__(self):
        with self.lock:
            available = self.max_count - len(self.timestamps)
            now = time.time()
            is_locked = now < self.lockout_until
            lockout_remaining = max(0, self.lockout_until - now)

        status = f"LOCKED({lockout_remaining:.1f}s)" if is_locked else "OK"
        return f"<RateLimiter max={self.max_count} window={self.time_window}s available={available} status={status}>"
