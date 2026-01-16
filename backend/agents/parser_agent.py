"""Parser Agent for content extraction"""

import logging
import os
from typing import Any, Dict

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.parser_tools import crawl4ai_parser_tool, docling_parser_tool

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    """Agent responsible for parsing web content and extracting textual information.

    This agent intelligently chooses between different parsing strategies:
    - Docling: Fast, works well for static HTML pages
    - Crawl4AI: Slower but handles JavaScript-heavy pages

    The agent can also handle OCR for images if configured.
    """

    def __init__(self):
        super().__init__(
            name="parser",
            role="Content Parser Specialist",
            goal="Extract clean, accurate textual content from any web source",
            backstory="""You are an expert in web scraping and content extraction with deep
            knowledge of HTML parsing, JavaScript rendering, and OCR technologies. You understand 
            the nuances of different web technologies and can choose the best extraction method 
            for any given URL.""",
        )

    def _execute_internal(self, task_description: str, context: Dict[str, Any]) -> str:
        """Execute parsing task

        Args:
            task_description: Description of the parsing task
            context: Must contain 'url' key with the URL to parse

        Returns:
            Extracted textual content

        Raises:
            ValueError: If URL is not provided
            Exception: If parsing fails
        """
        url = context.get("url")
        if not url:
            raise ValueError("URL is required for parsing")

        logger.info("Parser agent processing URL: %s", url)

        # Decide which parser to use based on configuration
        use_crawl4ai = (
            os.getenv("USE_CRAWL4AI_HEADLESS_BROWSER_HTML_PARSER", "false").lower()
            == "true"
        )

        try:
            if use_crawl4ai:
                logger.info("Using Crawl4AI parser (headless browser)")
                content = crawl4ai_parser_tool(url)
            else:
                logger.info("Using Docling parser (fast HTML parsing)")
                content = docling_parser_tool(url)

            if not content:
                raise ValueError("Parser returned empty content")

            logger.info("Successfully extracted %s characters", len(content))
            return content

        except Exception as e:
            logger.error("Parsing failed: %s", str(e))
            raise


# Made with Bob
