"""Crawl4AI-based HTML parser for web content extraction."""

import logging
import os
import re
from typing import Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crawl4AiHtmlParser:
    """
    A class to parse HTML content from a given URL using Crawl4AI,
    """

    def __init__(self, url: str, use_ocr: bool = False):
        self.url = url
        self.use_ocr: bool = (
            use_ocr  # TODO: Not used in this parser, but kept for consistency
        )
        self.crawl4ai_base_url = os.getenv("CRAWL4AI_BASE_URL")
        self.current_domain = self._extract_domain(url)

    @staticmethod
    def _extract_domain(url: str):
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except Exception as e:
            logger.warning("Failed to extract domain from url '%s': %s", url, e)
            return None

    @staticmethod
    def _extract_article_content_from_markdown(markdown: str) -> str:
        pattern = r"(?m)^#\s+(.+)"
        match = re.search(pattern, markdown, re.DOTALL)
        if match:
            return match.group(1)
        return markdown

    def _crawl4ai_payload(self):
        browser_config_payload = {
            "type": "BrowserConfig",
            "params": {
                "viewport_width": 1280,
                "viewport_height": 720,
                "headless": True,
                "light_mode": True,
                "text_mode": True,
            },
        }

        markdown_generator_payload = {
            "type": "DefaultMarkdownGenerator",
            "params": {
                "options": {
                    "ignore_links": True,
                }
            },
        }

        crawler_config_payload = {
            "type": "CrawlerRunConfig",
            "params": {
                "word_count_threshold": 10,
                "magic": True,
                "process_iframes": True,
                "wait_for": "css:body",
                "stream": False,
                "only_text": True,
                "scan_full_page": True,
                "cache_mode": "bypass",
                "exclude_external_images": False,
                "exclude_external_links": True,
                "exclude_domains": [self.current_domain] if self.current_domain else [],
                "excluded_tags": [
                    "nav",
                    "header",
                    "footer",
                    "aside",
                    "form",
                    "script",
                    "style",
                ],
                "remove_forms": True,
                "markdown_generator": markdown_generator_payload,
            },
        }

        return {
            "urls": [self.url],
            "priority": 10,
            "browser_config": browser_config_payload,
            "crawler_config": crawler_config_payload,
        }

    def get_textual_content(self) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.crawl4ai_base_url}/crawl",
                json=self._crawl4ai_payload(),
                timeout=30,
            )
            response.raise_for_status()
            output = response.json()

            success = output.get("success", False)
            if not success:
                logger.warning(
                    "Failed to extract blog content using crawl4ai: %s", output
                )
                return None

            results = output.get("results", [])
            if len(results) == 0:
                logger.warning("No results found using crawl4ai")
                return None

            result = results[0]
            if not result.get("success"):
                logger.warning(
                    "Failed to extract blog content using crawl4ai: %s", result
                )
                return None

            markdown = result.get("markdown", {}).get("markdown_with_citations")
            if not markdown:
                logger.warning("No markdown content found in crawl4ai response")
                return None

            return self._extract_article_content_from_markdown(markdown)

        except Exception as e:
            logger.warning("Failed to extract blog content using crawl4ai: %s", e)
            return None


# if __name__ == '__main__':
#     _url = "https://www.esentire.com/blog/mintsloader-stealc-and-boinc-delivery"
#     _parser = Crawl4AiHtmlParser(_url)
#     _content = _parser.get_textual_content()
#     if _content:
#         print("Extracted Content:")
#         print(_content)
#     else:
#         print("Failed to extract content.")
