"""
wecom_notifier.platforms - 平台实现模块

此模块包含各个通知平台的具体实现：
- wecom: 企业微信平台
- feishu: 飞书平台 (即将支持)

每个平台模块应提供：
1. 实现 SenderProtocol 的发送器适配器
2. 实现 MessageConverterProtocol 的消息转换器
3. 平台特定的常量和异常
"""

__all__ = []
