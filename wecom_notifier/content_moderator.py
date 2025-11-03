"""
内容审核器

整合敏感词加载、检测和策略应用
"""
from typing import Optional
from datetime import datetime

from .logger import get_logger
from .sensitive_word_loader import SensitiveWordLoader
from .content_filter import ContentFilter
from .moderation_strategies import create_strategy, ModerationStrategy
from .sensitive_logger import SensitiveMessageLogger


class ContentModerator:
    """
    内容审核器

    职责：
    1. 初始化时加载敏感词
    2. 提供审核接口
    3. 应用审核策略
    """

    def __init__(self, config: dict):
        """
        初始化审核器

        Args:
            config: 配置字典，包含：
                - sensitive_word_urls: List[str] - 敏感词URL列表
                - strategy: str - 审核策略 ("block" | "replace" | "pinyin_reverse")
                - cache_dir: str - 缓存目录
                - url_timeout: int - URL请求超时（秒）
                - log_sensitive_messages: bool - 是否记录敏感消息（默认True）
                - log_file: str - 日志文件路径
                - log_max_bytes: int - 单个日志文件最大字节数
                - log_backup_count: int - 保留的备份文件数量
        """
        self.logger = get_logger()
        self.config = config
        self.enabled = False
        self.sensitive_logger = None

        # 加载敏感词
        self.logger.info("Initializing content moderator...")
        word_loader = SensitiveWordLoader(config)
        words = word_loader.load()

        if not words:
            self.logger.warning("No sensitive words loaded, content moderation will be disabled")
            return

        # 初始化过滤器
        self.filter = ContentFilter()
        self.filter.load_words(words)

        # 创建策略
        strategy_name = config.get("strategy", "replace")
        self.strategy = create_strategy(strategy_name)
        self.strategy_name = strategy_name

        # 初始化敏感消息日志记录器（如果启用）
        if config.get("log_sensitive_messages", True):
            try:
                self.sensitive_logger = SensitiveMessageLogger(
                    log_file=config.get("log_file", ".wecom_cache/moderation.log"),
                    max_bytes=config.get("log_max_bytes", 10 * 1024 * 1024),
                    backup_count=config.get("log_backup_count", 5)
                )
                self.logger.info(f"Sensitive message logging enabled: {self.sensitive_logger.log_file}")
            except Exception as e:
                self.logger.error(f"Failed to initialize sensitive message logger: {e}")
                self.sensitive_logger = None

        self.enabled = True
        self.logger.info(f"Content moderator initialized with {len(words)} words, strategy: {strategy_name}")

    def moderate(self, content: str, message_id: str = None, msg_type: str = "text") -> Optional[str]:
        """
        审核内容

        Args:
            content: 待审核内容
            message_id: 消息ID（用于日志记录）
            msg_type: 消息类型（text/markdown_v2）

        Returns:
            Optional[str]: 审核后的内容，None表示拒绝发送
        """
        if not self.enabled:
            return content

        if not content:
            return content

        # 检测敏感词
        matches = self.filter.detect(content)

        if not matches:
            # 没有敏感词，直接返回
            return content

        # 有敏感词，应用策略
        self.logger.warning(f"Detected {len(matches)} sensitive word(s) in content")
        moderated_content = self.strategy.apply(content, matches)

        # 记录到日志
        if self.sensitive_logger and message_id:
            detected_words = list(set(match.word for match in matches))
            try:
                self.sensitive_logger.log_sensitive_message(
                    message_id=message_id,
                    content=content,
                    detected_words=detected_words,
                    strategy=self.strategy_name,
                    msg_type=msg_type
                )
            except Exception as e:
                self.logger.error(f"Failed to log sensitive message: {e}")

        return moderated_content

    def create_block_alert(self, content: str, message_id: str) -> str:
        """
        创建拒绝发送的提示消息

        Args:
            content: 原始内容
            message_id: 消息ID

        Returns:
            str: 提示消息
        """
        # 获取内容中的敏感词
        matches = self.filter.detect(content)
        detected_words = list(set(match.word for match in matches))

        # 去除敏感词后取前50字符作为预览
        preview = self._create_preview(content, matches)

        alert_message = f"""⚠️ 敏感内容已拦截

消息ID: {message_id}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
原始内容预览: {preview}"""

        return alert_message

    def _create_preview(self, content: str, matches: list, max_length: int = 50) -> str:
        """
        创建内容预览（去除敏感词）

        Args:
            content: 原始内容
            matches: 敏感词匹配列表
            max_length: 最大长度

        Returns:
            str: 预览文本
        """
        # 去除所有敏感词
        result = content
        sorted_matches = sorted(matches, key=lambda m: m.start_pos, reverse=True)

        for match in sorted_matches:
            result = result[:match.start_pos] + result[match.end_pos:]

        # 去除多余的空白
        result = ' '.join(result.split())

        # 截取前N个字符
        if len(result) > max_length:
            return result[:max_length] + "..."
        else:
            return result
