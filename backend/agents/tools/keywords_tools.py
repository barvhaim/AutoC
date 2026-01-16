"""Keywords extraction tools"""

import logging
from typing import List, Optional

from backend.extractors.keywords_extractor import KeywordsExtractor

logger = logging.getLogger(__name__)


def find_keywords_tool(content: str, keywords: Optional[List[str]] = None) -> List[str]:
    """Find relevant security keywords in the content.

    This tool searches for predefined security-related keywords in the given
    content. It performs case-insensitive matching and returns all found keywords.
    This is useful for quickly assessing if content is relevant to threat intelligence.

    Args:
        content: The textual content to search in
        keywords: Optional list of keywords to search for. If not provided,
                 uses default keywords from config.json

    Returns:
        List of keywords found in the content
    """
    try:
        logger.info("Searching for keywords in content (%s chars)", len(content))
        extractor = KeywordsExtractor(article_content=content, keywords=keywords or [])
        found_keywords = extractor.find_keywords_in_text()
        logger.info("Found %s keywords", len(found_keywords))
        return found_keywords
    except Exception as e:
        logger.error("Keywords extraction failed: %s", str(e))
        raise
