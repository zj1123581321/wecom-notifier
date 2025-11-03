"""
敏感词加载器

从URL加载敏感词列表，支持本地缓存
"""
import json
import os
from datetime import datetime
from typing import List, Optional
import requests

from .logger import get_logger


class SensitiveWordLoader:
    """敏感词加载器"""

    def __init__(self, config: dict):
        """
        初始化加载器

        Args:
            config: 配置字典，包含：
                - sensitive_word_urls: List[str] - 敏感词URL列表
                - cache_dir: str - 缓存目录
                - url_timeout: int - URL请求超时（秒）
        """
        self.logger = get_logger()
        self.urls = config.get("sensitive_word_urls", [])
        self.cache_dir = config.get("cache_dir", ".wecom_cache")
        self.timeout = config.get("url_timeout", 10)
        self.cache_file = os.path.join(self.cache_dir, "sensitive_words.json")

    def load(self) -> List[str]:
        """
        加载敏感词列表

        策略：
        1. 尝试从URL加载
        2. 如果成功且非空，更新缓存并返回
        3. 如果失败，尝试使用缓存
        4. 如果缓存也没有，返回空列表

        Returns:
            List[str]: 敏感词列表（去重、去空）
        """
        self.logger.info(f"Loading sensitive words from {len(self.urls)} URLs")

        # 1. 尝试从URL加载
        words = self._fetch_from_urls()

        if words:
            # 成功加载，更新缓存
            self.logger.info(f"Successfully loaded {len(words)} sensitive words from URLs")
            self._save_cache(words)
            return words
        else:
            # 加载失败，尝试使用缓存
            self.logger.warning("Failed to load from URLs, trying to use cache")
            cached_words = self._load_cache()
            if cached_words:
                self.logger.info(f"Using cached sensitive words: {len(cached_words)} words")
                return cached_words
            else:
                self.logger.error("No cache available, content moderation will be disabled")
                return []

    def _fetch_from_urls(self) -> List[str]:
        """
        从URL列表加载敏感词

        Returns:
            List[str]: 敏感词列表（合并去重）
        """
        all_words = set()

        for url in self.urls:
            try:
                self.logger.debug(f"Fetching sensitive words from: {url}")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()

                # 解析文本内容
                content = response.text
                words = self._parse_content(content)
                all_words.update(words)
                self.logger.debug(f"Loaded {len(words)} words from {url}")

            except requests.RequestException as e:
                self.logger.error(f"Failed to fetch from {url}: {e}")
            except Exception as e:
                self.logger.error(f"Error processing {url}: {e}")

        return list(all_words)

    def _parse_content(self, content: str) -> List[str]:
        """
        解析敏感词文本内容

        规则：
        - 每行一个词
        - 去除空行
        - 去除行首行尾空格
        - 支持注释行（以#开头）

        Args:
            content: 文本内容

        Returns:
            List[str]: 敏感词列表
        """
        words = []
        for line in content.splitlines():
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            words.append(line)
        return words

    def _save_cache(self, words: List[str]):
        """
        保存敏感词到缓存文件

        Args:
            words: 敏感词列表
        """
        try:
            # 确保缓存目录存在
            os.makedirs(self.cache_dir, exist_ok=True)

            cache_data = {
                "version": "1.0",
                "last_update": datetime.now().isoformat(),
                "source_urls": self.urls,
                "word_count": len(words),
                "words": words
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"Saved {len(words)} words to cache: {self.cache_file}")

        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def _load_cache(self) -> Optional[List[str]]:
        """
        从缓存文件加载敏感词

        Returns:
            Optional[List[str]]: 敏感词列表，失败返回None
        """
        try:
            if not os.path.exists(self.cache_file):
                self.logger.debug("Cache file does not exist")
                return None

            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            words = cache_data.get("words", [])
            last_update = cache_data.get("last_update", "unknown")
            self.logger.debug(f"Loaded {len(words)} words from cache (last update: {last_update})")

            return words

        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            return None
