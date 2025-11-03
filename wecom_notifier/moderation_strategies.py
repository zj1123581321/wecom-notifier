"""
内容审核策略

实现三种审核策略：
1. BlockStrategy - 拒绝发送
2. ReplaceStrategy - 替换为[敏感词]
3. PinyinReverseStrategy - 拼音/字母倒置
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from pypinyin import lazy_pinyin
import re

from .logger import get_logger
from .content_filter import ContentFilter, SensitiveWordMatch

# 模块级别的 logger
logger = get_logger()


class ModerationStrategy(ABC):
    """审核策略基类"""

    @abstractmethod
    def apply(self, content: str, matches: List[SensitiveWordMatch]) -> Optional[str]:
        """
        应用审核策略

        Args:
            content: 原始内容
            matches: 检测到的敏感词匹配列表

        Returns:
            Optional[str]: 处理后的内容，None表示拒绝发送
        """
        pass


class BlockStrategy(ModerationStrategy):
    """
    拒绝发送策略

    如果检测到敏感词，直接拒绝发送
    """

    def apply(self, content: str, matches: List[SensitiveWordMatch]) -> Optional[str]:
        """
        应用拒绝策略

        Args:
            content: 原始内容
            matches: 检测到的敏感词匹配列表

        Returns:
            None: 始终返回None，表示拒绝发送
        """
        if matches:
            logger.warning(f"Content blocked due to {len(matches)} sensitive word(s)")
            return None
        return content


class ReplaceStrategy(ModerationStrategy):
    """
    替换策略

    将敏感词替换为固定字符串 [敏感词]
    """

    def __init__(self, replacement: str = "[敏感词]"):
        """
        Args:
            replacement: 替换字符串（默认"[敏感词]"）
        """
        self.replacement = replacement

    def apply(self, content: str, matches: List[SensitiveWordMatch]) -> Optional[str]:
        """
        应用替换策略

        Args:
            content: 原始内容
            matches: 检测到的敏感词匹配列表

        Returns:
            str: 替换后的内容
        """
        if not matches:
            return content

        # 按位置从后往前排序，避免替换时位置偏移
        sorted_matches = sorted(matches, key=lambda m: m.start_pos, reverse=True)

        result = content
        for match in sorted_matches:
            # 替换敏感词
            result = (
                result[:match.start_pos] +
                self.replacement +
                result[match.end_pos:]
            )

        logger.info(f"Replaced {len(matches)} sensitive word(s)")
        return result


class PinyinReverseStrategy(ModerationStrategy):
    """
    拼音/字母倒置策略

    - 中文：提取拼音首字母倒置
    - 英文：整个单词字母倒置
    - 数字/特殊字符：保持原样
    """

    def apply(self, content: str, matches: List[SensitiveWordMatch]) -> Optional[str]:
        """
        应用拼音倒置策略

        Args:
            content: 原始内容
            matches: 检测到的敏感词匹配列表

        Returns:
            str: 处理后的内容
        """
        if not matches:
            return content

        # 按位置从后往前排序，避免替换时位置偏移
        sorted_matches = sorted(matches, key=lambda m: m.start_pos, reverse=True)

        result = content
        for match in sorted_matches:
            original_word = content[match.start_pos:match.end_pos]
            reversed_word = self._reverse_word(original_word)

            result = (
                result[:match.start_pos] +
                reversed_word +
                result[match.end_pos:]
            )

        logger.info(f"Reversed {len(matches)} sensitive word(s)")
        return result

    def _reverse_word(self, word: str) -> str:
        """
        倒置单个词

        处理逻辑：
        1. 识别连续的中文字符、英文字符、其他字符
        2. 分别处理：
           - 中文：提取拼音首字母并倒置
           - 英文：字母倒置
           - 其他：保持原样
        3. 合并结果

        Args:
            word: 原始词

        Returns:
            str: 倒置后的词
        """
        if not word:
            return word

        # 分段处理
        segments = self._segment_word(word)
        reversed_segments = []

        for seg_type, seg_text in segments:
            if seg_type == 'chinese':
                # 中文：拼音首字母倒置
                reversed_segments.append(self._reverse_chinese(seg_text))
            elif seg_type == 'english':
                # 英文：字母倒置
                reversed_segments.append(seg_text[::-1])
            else:
                # 其他：保持原样
                reversed_segments.append(seg_text)

        return ''.join(reversed_segments)

    def _segment_word(self, word: str) -> List[tuple]:
        """
        将词分段为连续的中文、英文、其他字符

        Args:
            word: 原始词

        Returns:
            List[tuple]: [(类型, 文本), ...]
        """
        segments = []
        current_type = None
        current_text = []

        for char in word:
            if '\u4e00' <= char <= '\u9fff':
                char_type = 'chinese'
            elif char.isalpha():
                char_type = 'english'
            else:
                char_type = 'other'

            if char_type == current_type:
                current_text.append(char)
            else:
                if current_text:
                    segments.append((current_type, ''.join(current_text)))
                current_type = char_type
                current_text = [char]

        # 添加最后一段
        if current_text:
            segments.append((current_type, ''.join(current_text)))

        return segments

    def _reverse_chinese(self, text: str) -> str:
        """
        处理中文：提取拼音首字母并倒置

        Args:
            text: 中文文本

        Returns:
            str: 拼音首字母倒置结果
        """
        # 获取拼音列表
        pinyin_list = lazy_pinyin(text)

        # 提取首字母
        initials = [py[0] for py in pinyin_list]

        # 倒置
        reversed_initials = initials[::-1]

        return ''.join(reversed_initials)


def create_strategy(strategy_name: str, **kwargs) -> ModerationStrategy:
    """
    创建审核策略

    Args:
        strategy_name: 策略名称 ("block" | "replace" | "pinyin_reverse")
        **kwargs: 策略参数

    Returns:
        ModerationStrategy: 策略实例

    Raises:
        ValueError: 未知的策略名称
    """
    if strategy_name == "block":
        return BlockStrategy()
    elif strategy_name == "replace":
        replacement = kwargs.get("replacement", "[敏感词]")
        return ReplaceStrategy(replacement)
    elif strategy_name == "pinyin_reverse":
        return PinyinReverseStrategy()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
