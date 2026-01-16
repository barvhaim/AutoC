"""Keywords extraction module for security content analysis."""

import json
from typing import List, Optional


class KeywordsExtractor:
    def __init__(self, article_content: str, keywords: Optional[List[str]] = None):
        self.article_content = article_content
        self.keywords = keywords if keywords else self._load_keywords()

    @staticmethod
    def _load_keywords() -> List[str]:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
            keywords = list(set(config["keywords"]))
        return keywords

    def find_keywords_in_text(self) -> List[str]:
        text_lower = self.article_content.lower()
        keywords_lower = [keyword.lower() for keyword in self.keywords]
        found_keywords = [
            keyword for keyword in keywords_lower if keyword in text_lower
        ]
        return found_keywords
