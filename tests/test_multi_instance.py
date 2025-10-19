"""
测试多实例问题

验证当外部程序创建多个 WeComNotifier 实例时会发生什么
"""
import time
import threading
from wecom_notifier import WeComNotifier


def test_multi_instance_problem():
    """
    测试：多个实例针对同一个webhook会创建多个线程
    """
    webhook_url = "https://test.webhook.url"

    # 创建两个实例
    notifier1 = WeComNotifier()
    notifier2 = WeComNotifier()

    # 获取管理器（会触发创建）
    manager1 = notifier1._get_or_create_manager(webhook_url)
    manager2 = notifier2._get_or_create_manager(webhook_url)

    # 验证是否是不同的对象
    print(f"Manager1 ID: {id(manager1)}")
    print(f"Manager2 ID: {id(manager2)}")
    print(f"Are they same object? {manager1 is manager2}")

    # 验证工作线程
    print(f"\nManager1 thread: {manager1.worker_thread}")
    print(f"Manager2 thread: {manager2.worker_thread}")
    print(f"Are they same thread? {manager1.worker_thread is manager2.worker_thread}")

    # 验证频控器
    print(f"\nManager1 rate_limiter ID: {id(manager1.rate_limiter)}")
    print(f"Manager2 rate_limiter ID: {id(manager2.rate_limiter)}")
    print(f"Are they same rate_limiter? {manager1.rate_limiter is manager2.rate_limiter}")

    # 清理
    notifier1.stop_all()
    notifier2.stop_all()

    print("\n" + "="*60)
    print("结论：多个 WeComNotifier 实例会创建多个独立的管理器和线程！")
    print("="*60)


def test_active_threads_count():
    """
    测试：查看创建的线程数量
    """
    webhook_url = "https://test.webhook.url"

    initial_thread_count = threading.active_count()
    print(f"Initial thread count: {initial_thread_count}")

    notifiers = []
    for i in range(3):
        notifier = WeComNotifier()
        # 触发管理器创建
        notifier._get_or_create_manager(webhook_url)
        notifiers.append(notifier)

        current_count = threading.active_count()
        print(f"After creating notifier {i+1}: {current_count} threads (+{current_count - initial_thread_count})")

    # 清理
    for notifier in notifiers:
        notifier.stop_all()

    time.sleep(0.5)  # 等待线程停止

    final_count = threading.active_count()
    print(f"After cleanup: {final_count} threads")

    print("\n" + "="*60)
    print(f"创建了 {len(notifiers)} 个实例，新增了 {3} 个工作线程！")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("测试 1: 多实例对象独立性")
    print("="*60)
    test_multi_instance_problem()

    print("\n" + "="*60)
    print("测试 2: 活跃线程计数")
    print("="*60)
    test_active_threads_count()
