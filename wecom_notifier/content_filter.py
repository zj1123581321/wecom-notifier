"""
内容过滤器

使用AC自动机算法高效检测敏感词
"""
from typing import List, Tuple
import ahocorasick

from .logger import get_logger


class SensitiveWordMatch:
    """敏感词匹配结果"""

    def __init__(self, word: str, start_pos: int, end_pos: int):
        """
        Args:
            word: 匹配到的敏感词
            start_pos: 起始位置
            end_pos: 结束位置
        """
        self.word = word
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return f"<Match word='{self.word}' pos=[{self.start_pos}:{self.end_pos}]>"


class ContentFilter:
    """
    内容过滤器

    使用AC自动机算法进行高效的敏感词检测
    特性：
    - 部分匹配（子串匹配）
    - 大小写不敏感
    - O(n)时间复杂度，与敏感词数量无关
    """

    def __init__(self):
        """初始化过滤器"""
        self.logger = get_logger()
        self.automaton: ahocorasick.Automaton = None
        self.word_count = 0

    def load_words(self, words: List[str]):
        """
        加载敏感词列表

        Args:
            words: 敏感词列表
        """
        if not words:
            self.logger.warning("No sensitive words to load")
            return

        self.logger.info(f"Building AC automaton with {len(words)} words")

        # 创建AC自动机
        self.automaton = ahocorasick.Automaton()

        # 添加敏感词（小写化处理，大小写不敏感）
        for word in words:
            if not word:
                continue
            word_lower = word.lower()
            # 存储小写版本作为key，原始词作为value
            self.automaton.add_word(word_lower, word)

        # 构建自动机
        self.automaton.make_automaton()
        self.word_count = len(words)

        self.logger.info(f"AC automaton built successfully with {self.word_count} words")

    def detect(self, content: str) -> List[SensitiveWordMatch]:
        """
        检测内容中的敏感词

        Args:
            content: 待检测内容

        Returns:
            List[SensitiveWordMatch]: 匹配到的敏感词列表
        """
        if not self.automaton:
            self.logger.warning("AC automaton not initialized, skipping detection")
            return []

        if not content:
            return []

        matches = []
        content_lower = content.lower()

        # 使用AC自动机查找所有匹配
        for end_pos, original_word in self.automaton.iter(content_lower):
            # end_pos 是匹配结束位置（inclusive）
            start_pos = end_pos - len(original_word) + 1
            match = SensitiveWordMatch(
                word=original_word,
                start_pos=start_pos,
                end_pos=end_pos + 1  # 转换为exclusive
            )
            matches.append(match)

        if matches:
            self.logger.debug(f"Detected {len(matches)} sensitive word(s) in content")

        return matches

    def has_sensitive_word(self, content: str) -> bool:
        """
        检查内容是否包含敏感词

        Args:
            content: 待检测内容

        Returns:
            bool: 是否包含敏感词
        """
        return len(self.detect(content)) > 0

    def get_unique_words(self, content: str) -> List[str]:
        """
        获取内容中的所有唯一敏感词

        Args:
            content: 待检测内容

        Returns:
            List[str]: 去重的敏感词列表
        """
        matches = self.detect(content)
        unique_words = list(set(match.word for match in matches))
        return unique_words
