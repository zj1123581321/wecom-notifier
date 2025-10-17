"""
消息分段器 - 智能分段逻辑
"""
import re
from typing import List
from .models import SegmentInfo
from .constants import (
    MAX_BYTES_PER_MESSAGE,
    MSG_TYPE_TEXT,
    MSG_TYPE_MARKDOWN_V2,
    MARKDOWN_TABLE_ROW_PATTERN,
    SEGMENT_CONTINUE_PREFIX,
    SEGMENT_CONTINUE_SUFFIX
)


class MessageSegmenter:
    """消息分段器"""

    def __init__(self, max_bytes: int = MAX_BYTES_PER_MESSAGE):
        """
        初始化分段器

        Args:
            max_bytes: 每条消息的最大字节数
        """
        self.max_bytes = max_bytes

    def segment(self, content: str, msg_type: str) -> List[SegmentInfo]:
        """
        对消息内容进行分段

        Args:
            content: 消息内容
            msg_type: 消息类型

        Returns:
            List[SegmentInfo]: 分段列表
        """
        # 检查是否需要分段
        if len(content.encode('utf-8')) <= self.max_bytes:
            return [SegmentInfo(content, is_first=True, is_last=True)]

        # 根据消息类型选择分段策略
        if msg_type == MSG_TYPE_TEXT:
            segments = self._segment_text(content)
        elif msg_type == MSG_TYPE_MARKDOWN_V2:
            segments = self._segment_markdown(content)
        else:
            # 其他类型（如image）不需要文本分段
            segments = [content]

        # 标记首尾
        return self._mark_segments(segments)

    def _segment_text(self, content: str) -> List[str]:
        """
        文本类型的简单分段

        策略：按行分割，尽量填满每个分段
        """
        segments = []
        current = ""
        lines = content.split('\n')

        for line in lines:
            test_content = current + ('\n' if current else '') + line

            if len(test_content.encode('utf-8')) > self.max_bytes:
                # 当前行加入会超限
                if current:
                    segments.append(current)
                    current = line
                else:
                    # 单行就超过限制，强制截断
                    chunks = self._force_split(line, self.max_bytes)
                    segments.extend(chunks[:-1])
                    current = chunks[-1]
            else:
                current = test_content

        if current:
            segments.append(current)

        return segments

    def _segment_markdown(self, content: str) -> List[str]:
        """
        Markdown类型的智能分段

        策略：
        1. 按双换行符分段（段落）
        2. 识别特殊元素（表格、代码块）并保护
        3. 尽量填满每个分段，但不破坏语法
        """
        segments = []
        current = ""

        # 先处理代码块（暂时替换为占位符）
        code_blocks = []
        content = self._extract_code_blocks(content, code_blocks)

        # 按段落分割
        paragraphs = content.split('\n\n')

        i = 0
        while i < len(paragraphs):
            para = paragraphs[i]

            # 还原代码块
            para = self._restore_code_blocks(para, code_blocks)

            # 检查是否是表格
            if self._is_table_start(para):
                # 处理表格
                table_paras = [para]
                i += 1
                while i < len(paragraphs) and self._is_table_row(paragraphs[i]):
                    table_paras.append(paragraphs[i])
                    i += 1

                table_content = '\n\n'.join(table_paras)
                table_content = self._restore_code_blocks(table_content, code_blocks)

                # 处理表格分段
                table_segments = self._segment_table(table_content)
                for seg in table_segments:
                    if current and len((current + '\n\n' + seg).encode('utf-8')) > self.max_bytes:
                        segments.append(current)
                        current = seg
                    elif not current:
                        current = seg
                    else:
                        current += '\n\n' + seg
                continue

            # 普通段落
            test_content = current + ('\n\n' if current else '') + para

            if len(test_content.encode('utf-8')) > self.max_bytes:
                if current:
                    segments.append(current)
                    current = para
                else:
                    # 单个段落就超过限制
                    if self._is_protected_element(para):
                        # 保护元素，强制截断
                        chunks = self._force_split(para, self.max_bytes)
                        segments.extend(chunks[:-1])
                        current = chunks[-1]
                    else:
                        # 普通段落，按行分割
                        line_segments = self._segment_text(para)
                        segments.extend(line_segments[:-1])
                        current = line_segments[-1]
            else:
                current = test_content

            i += 1

        if current:
            segments.append(current)

        return segments

    def _segment_table(self, table_content: str) -> List[str]:
        """
        分段表格，保留表头

        Args:
            table_content: 表格内容

        Returns:
            List[str]: 表格分段列表
        """
        lines = table_content.split('\n')

        # 提取表头（前两行：标题行 + 分隔行）
        if len(lines) < 3:
            return [table_content]

        header = '\n'.join(lines[:2])
        data_rows = lines[2:]

        # 检查表头大小
        header_bytes = len(header.encode('utf-8'))
        if header_bytes > self.max_bytes:
            # 表头本身就超限，强制截断
            return self._force_split(table_content, self.max_bytes)

        segments = []
        current_rows = []

        # 预留续页提示的空间
        from .constants import SEGMENT_CONTINUE_PREFIX, SEGMENT_CONTINUE_SUFFIX
        reserved_bytes = len(SEGMENT_CONTINUE_PREFIX.encode('utf-8')) + len(SEGMENT_CONTINUE_SUFFIX.encode('utf-8'))

        # 可用字节数 = 总限制 - 表头 - 换行符 - 续页提示
        available_bytes = self.max_bytes - header_bytes - len('\n'.encode('utf-8')) - reserved_bytes

        for row in data_rows:
            row_bytes = len(row.encode('utf-8')) + len('\n'.encode('utf-8'))

            if sum(len(r.encode('utf-8')) + len('\n'.encode('utf-8')) for r in current_rows) + row_bytes <= available_bytes:
                current_rows.append(row)
            else:
                if current_rows:
                    # 生成分段
                    seg = header + '\n' + '\n'.join(current_rows)
                    segments.append(seg)
                    current_rows = [row]
                else:
                    # 单行就超限，强制截断
                    segments.append(header + '\n' + row)

        if current_rows:
            seg = header + '\n' + '\n'.join(current_rows)
            segments.append(seg)

        return segments

    def _extract_code_blocks(self, content: str, code_blocks: List[str]) -> str:
        """提取代码块，替换为占位符"""

        def replacer(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

        return re.sub(r'```[\s\S]*?```', replacer, content)

    def _restore_code_blocks(self, content: str, code_blocks: List[str]) -> str:
        """还原代码块"""
        for i, block in enumerate(code_blocks):
            content = content.replace(f"__CODE_BLOCK_{i}__", block)
        return content

    def _is_table_start(self, para: str) -> bool:
        """判断是否是表格开始"""
        lines = para.strip().split('\n')
        if len(lines) < 2:
            return False

        # 检查第一行和第二行是否都是表格行
        # 第二行应该是分隔行（如 |---|---|）
        return (re.match(MARKDOWN_TABLE_ROW_PATTERN, lines[0].strip()) and
                re.match(r'^\|[\s:-]+\|', lines[1].strip()))

    def _is_table_row(self, para: str) -> bool:
        """判断是否是表格行"""
        return bool(re.match(MARKDOWN_TABLE_ROW_PATTERN, para.strip()))

    def _is_protected_element(self, para: str) -> bool:
        """判断是否是需要保护的元素（链接、图片、代码块）"""
        # 代码块
        if para.strip().startswith('```') and para.strip().endswith('```'):
            return True

        # 图片
        if re.match(r'^!\[.*?\]\(.*?\)$', para.strip()):
            return True

        return False

    def _force_split(self, text: str, max_bytes: int) -> List[str]:
        """
        强制按字节截断文本

        Args:
            text: 文本内容
            max_bytes: 最大字节数

        Returns:
            List[str]: 分段列表
        """
        segments = []
        current = ""

        for char in text:
            test = current + char
            if len(test.encode('utf-8')) > max_bytes:
                if current:
                    segments.append(current)
                    current = char
                else:
                    # 单个字符就超限（理论上不会发生）
                    segments.append(char)
            else:
                current = test

        if current:
            segments.append(current)

        return segments

    def _mark_segments(self, segments: List[str]) -> List[SegmentInfo]:
        """
        标记分段的首尾，并添加续页提示

        Args:
            segments: 原始分段列表

        Returns:
            List[SegmentInfo]: 带标记的分段列表
        """
        if not segments:
            return []

        result = []
        for i, seg in enumerate(segments):
            is_first = (i == 0)
            is_last = (i == len(segments) - 1)

            # 添加续页提示
            content = seg
            if not is_first:
                content = SEGMENT_CONTINUE_PREFIX + content
            if not is_last:
                content = content + SEGMENT_CONTINUE_SUFFIX

            result.append(SegmentInfo(content, is_first, is_last))

        return result
