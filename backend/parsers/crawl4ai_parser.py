import logging
from dotenv import load_dotenv
from typing import Optional
import requests
import os
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crawl4AIParser:
    def __init__(self, url: str, use_ocr: bool = False):
        self.url = url
        self.use_ocr: bool = use_ocr
        self.crawl4ai_base_url = os.getenv("CRAWL4AI_BASE_URL")

    @staticmethod
    def _extract_article_content_from_markdown(markdown: str) -> str:
        # Regex to match the title and everything after it, TODO: improve method (?)
        pattern = r"(# .*)"
        match = re.search(pattern, markdown, re.DOTALL)
        if match:
            return match.group(1)
        return markdown

    def _crawl4ai_payload(self):
        return {
            "urls": [self.url],
            "priority": 10,
        }

    def get_textual_content(self) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.crawl4ai_base_url}/crawl", json=self._crawl4ai_payload()
            )
            response.raise_for_status()
            output = response.json()

            success = output.get("success", False)
            if not success:
                logger.warning(
                    f"Failed to extract blog content using crawl4ai: {output}"
                )
                return None

            results = output.get("results", [])
            if len(results) == 0:
                logger.warning("No results found using crawl4ai")
                return None

            result = results[0]
            if result.get("status_code") != 200 or result.get("success") != True:
                logger.warning(
                    f"Failed to extract blog content using crawl4ai: {result}"
                )
                return None

            content = result.get("markdown", {}).get("markdown_with_citations")
            if not content:
                logger.warning("Failed to extract blog content using crawl4ai")
                return None

            return self._extract_article_content_from_markdown(content)

        except Exception as e:
            logger.warning(f"Failed to extract blog content using crawl4ai: {e}")
            return None
