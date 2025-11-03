"""
敏感消息日志记录器

记录包含敏感词的消息，用于审计和追溯
"""
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import List


class SensitiveMessageLogger:
    """
    敏感消息日志记录器

    使用JSON Lines格式记录包含敏感词的消息
    支持日志轮转，防止文件过大
    """

    def __init__(
        self,
        log_file: str = ".wecom_cache/moderation.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        初始化日志记录器

        Args:
            log_file: 日志文件路径
            max_bytes: 单个日志文件最大字节数（默认10MB）
            backup_count: 保留的备份文件数量（默认5个）
        """
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 创建独立的 logger
        self.logger = logging.getLogger('wecom_sensitive_messages')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # 不传播到父logger

        # 如果已经有handler，先清除（避免重复添加）
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 添加 RotatingFileHandler
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # 设置格式（只输出消息本身，不要时间戳等前缀，因为我们用JSON格式）
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # 设置文件权限（仅所有者可读写）
        try:
            os.chmod(log_file, 0o600)
        except Exception:
            pass  # Windows可能不支持，忽略

    def log_sensitive_message(
        self,
        message_id: str,
        content: str,
        detected_words: List[str],
        strategy: str,
        msg_type: str
    ):
        """
        记录敏感消息

        Args:
            message_id: 消息ID
            content: 原始内容（完整）
            detected_words: 检测到的敏感词列表
            strategy: 应用的策略（block/replace/pinyin_reverse）
            msg_type: 消息类型（text/markdown_v2）
        """
        # 构造日志记录（JSON格式）
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "message_id": message_id,
            "strategy": strategy,
            "msg_type": msg_type,
            "detected_words": detected_words,
            "original_content": content
        }

        # 写入日志（JSON Lines格式，每行一个JSON对象）
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def get_log_file_info(self) -> dict:
        """
        获取日志文件信息

        Returns:
            dict: 包含文件路径、大小等信息
        """
        info = {
            "log_file": self.log_file,
            "max_bytes": self.max_bytes,
            "backup_count": self.backup_count,
            "exists": os.path.exists(self.log_file),
        }

        if info["exists"]:
            info["current_size"] = os.path.getsize(self.log_file)
            info["current_size_mb"] = round(info["current_size"] / (1024 * 1024), 2)

        return info
