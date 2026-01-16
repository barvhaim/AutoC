"""Parser tools for content extraction"""

import logging
import os

from backend.parsers.crawl4ai_html_parser import Crawl4AiHtmlParser
from backend.parsers.html_parser import HtmlParser

logger = logging.getLogger(__name__)


def docling_parser_tool(url: str) -> str:
    """Extract textual content from URL using Docling parser.

    This tool uses the Docling library combined with BeautifulSoup to parse
    HTML content and extract clean textual information. It's fast and works
    well for most static web pages.

    Args:
        url: The URL to extract content from

    Returns:
        Clean textual content extracted from the page
    """
    try:
        logger.info("Extracting content from %s using Docling", url)
        use_ocr = os.getenv("ANALYZE_BLOG_IMAGES", "false").lower() == "true"
        parser = HtmlParser(url=url, use_ocr=use_ocr)
        content = parser.get_textual_content()
        logger.info("Successfully extracted %s characters", len(content))
        return content
    except Exception as e:
        logger.error("Docling parser failed: %s", str(e))
        raise


def crawl4ai_parser_tool(url: str) -> str:
    """Extract textual content from URL using Crawl4AI headless browser.

    This tool uses a headless browser to render JavaScript-heavy pages and
    extract content. It's more reliable for dynamic websites but slower than
    Docling. Use this when the page requires JavaScript execution.

    Args:
        url: The URL to extract content from

    Returns:
        Clean textual content extracted from the page
    """
    try:
        logger.info("Extracting content from %s using Crawl4AI", url)
        use_ocr = os.getenv("ANALYZE_BLOG_IMAGES", "false").lower() == "true"
        parser = Crawl4AiHtmlParser(url=url, use_ocr=use_ocr)
        content = parser.get_textual_content()
        logger.info("Successfully extracted %s characters", len(content))
        return content
    except Exception as e:
        logger.error("Crawl4AI parser failed: %s", str(e))
        raise


# Made with Bob
