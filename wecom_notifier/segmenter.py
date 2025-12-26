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
    PAGE_INDICATOR_FORMAT,
    MAX_PAGE_INDICATOR_BYTES
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

        # 预留页码标记的空间
        reserved_bytes = MAX_PAGE_INDICATOR_BYTES
        available_bytes = self.max_bytes - reserved_bytes

        for line in lines:
            test_content = current + ('\n' if current else '') + line

            if len(test_content.encode('utf-8')) > available_bytes:
                # 当前行加入会超限
                if current:
                    segments.append(current)
                    current = line
                else:
                    # 单行就超过限制，强制截断
                    chunks = self._force_split(line, available_bytes)
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

        # 预留页码标记的空间
        reserved_bytes = MAX_PAGE_INDICATOR_BYTES
        available_bytes = self.max_bytes - reserved_bytes

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

            # 检查是否是表格（段落开头就是表格）
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
                    if current and len((current + '\n\n' + seg).encode('utf-8')) > available_bytes:
                        segments.append(current)
                        current = seg
                    elif not current:
                        current = seg
                    else:
                        current += '\n\n' + seg
                continue

            # 检查段落中间是否包含表格（表格前有文字的情况）
            table_start_idx = self._find_table_in_paragraph(para)
            if table_start_idx > 0:
                # 分离表格前的文字和表格部分
                lines = para.split('\n')
                prefix_text = '\n'.join(lines[:table_start_idx])
                table_content = '\n'.join(lines[table_start_idx:])

                # 收集后续的表格行
                i += 1
                while i < len(paragraphs) and self._is_table_row(paragraphs[i]):
                    table_content += '\n\n' + paragraphs[i]
                    i += 1

                table_content = self._restore_code_blocks(table_content, code_blocks)

                # 先处理前缀文字
                test_content = current + ('\n\n' if current else '') + prefix_text
                if len(test_content.encode('utf-8')) > available_bytes:
                    if current:
                        segments.append(current)
                    current = prefix_text
                else:
                    current = test_content

                # 处理表格分段（保留表头）
                table_segments = self._segment_table(table_content)
                for seg in table_segments:
                    if current and len((current + '\n' + seg).encode('utf-8')) > available_bytes:
                        segments.append(current)
                        current = seg
                    elif not current:
                        current = seg
                    else:
                        current += '\n' + seg
                continue

            # 普通段落
            test_content = current + ('\n\n' if current else '') + para

            if len(test_content.encode('utf-8')) > available_bytes:
                if current:
                    # 检查 current 末尾是否有孤立标题，避免标题与正文分离
                    content_without_heading, trailing_heading = self._extract_trailing_heading(current)

                    if trailing_heading and content_without_heading:
                        # 有末尾标题且前面有其他内容
                        # 回溯：只保存标题之前的内容，标题留给下一段
                        segments.append(content_without_heading)
                        current = trailing_heading
                        # 不增加 i，重新处理当前 para（让标题和正文有机会合并）
                        continue

                    # 没有需要回溯的标题，正常分段
                    segments.append(current)
                    current = ""
                    # 重新检查para本身是否超限
                    if len(para.encode('utf-8')) > available_bytes:
                        # para本身超限，需要分段
                        if self._is_protected_element(para):
                            chunks = self._force_split(para, available_bytes)
                            segments.extend(chunks[:-1])
                            current = chunks[-1]
                        else:
                            line_segments = self._segment_text(para)
                            segments.extend(line_segments[:-1])
                            current = line_segments[-1]
                    else:
                        current = para
                else:
                    # 单个段落就超过限制
                    if self._is_protected_element(para):
                        # 保护元素，强制截断
                        chunks = self._force_split(para, available_bytes)
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

        # 预留页码标记的空间
        reserved_bytes = MAX_PAGE_INDICATOR_BYTES

        # 可用字节数 = 总限制 - 表头 - 换行符 - 页码标记
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

    def _is_heading(self, text: str) -> bool:
        """判断文本是否是 Markdown 标题（# 到 ###### 开头）"""
        stripped = text.strip()
        return bool(re.match(r'^#{1,6}\s+', stripped))

    def _extract_trailing_heading(self, content: str) -> tuple:
        """
        提取内容末尾的标题

        Args:
            content: 当前累积的内容

        Returns:
            tuple: (不含标题的内容, 标题) 或 (原内容, None) 如果没有末尾标题
        """
        if not content:
            return (content, None)

        # 按段落分割（双换行）
        parts = content.rsplit('\n\n', 1)

        if len(parts) == 2:
            before, last_para = parts
            # 检查最后一个段落是否是标题
            if self._is_heading(last_para):
                return (before, last_para)
        elif len(parts) == 1:
            # 只有一个段落，检查它是否是标题
            if self._is_heading(parts[0]):
                # 整个内容就是一个标题，返回空和标题
                return ('', parts[0])

        return (content, None)

    def _is_table_start(self, para: str) -> bool:
        """判断是否是表格开始"""
        lines = para.strip().split('\n')
        if len(lines) < 2:
            return False

        # 检查第一行和第二行是否都是表格行
        # 第二行应该是分隔行（如 |---|---|）
        return (re.match(MARKDOWN_TABLE_ROW_PATTERN, lines[0].strip()) and
                re.match(r'^\|[\s:-]+\|', lines[1].strip()))

    def _find_table_in_paragraph(self, para: str) -> int:
        """
        在段落中查找表格的起始行索引

        Args:
            para: 段落内容

        Returns:
            int: 表格起始行索引，如果没找到返回 -1
        """
        lines = para.split('\n')
        for i in range(len(lines) - 1):
            # 检查第 i 行是否是表格标题行，第 i+1 行是否是分隔行
            if (re.match(MARKDOWN_TABLE_ROW_PATTERN, lines[i].strip()) and
                re.match(r'^\|[\s:-]+\|', lines[i + 1].strip())):
                return i
        return -1

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
        标记分段的首尾，并添加页码标记

        Args:
            segments: 原始分段列表

        Returns:
            List[SegmentInfo]: 带标记的分段列表
        """
        if not segments:
            return []

        total_pages = len(segments)
        result = []

        for i, seg in enumerate(segments):
            is_first = (i == 0)
            is_last = (i == len(segments) - 1)
            page_number = i + 1  # 页码从1开始

            # 仅当总页数 > 1 时添加页码标记
            content = seg
            if total_pages > 1:
                page_indicator = PAGE_INDICATOR_FORMAT.format(
                    current=page_number,
                    total=total_pages
                )
                content = page_indicator + content

            # 创建 SegmentInfo，包含页码信息（方便调试）
            segment_info = SegmentInfo(
                content=content,
                is_first=is_first,
                is_last=is_last,
                page_number=page_number if total_pages > 1 else None,
                total_pages=total_pages if total_pages > 1 else None
            )
            result.append(segment_info)

        return result
