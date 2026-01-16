"""Keywords Intelligence Agent for security keyword identification"""

import logging
from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.keywords_tools import find_keywords_tool

logger = logging.getLogger(__name__)


class KeywordsAgent(BaseAgent):
    """Agent responsible for identifying security-related keywords in content.

    This agent searches for predefined security keywords to quickly assess
    content relevance for threat intelligence analysis. It performs case-insensitive
    matching and can work with custom keyword lists.
    """

    def __init__(self):
        super().__init__(
            name="keywords",
            role="Keywords Intelligence Analyst",
            goal="Identify all relevant security keywords and assess content relevance",
            backstory="""You are a cybersecurity analyst specialized in threat intelligence
            keyword analysis. You have deep knowledge of security terminology, malware families, 
            attack techniques, and threat actor nomenclature. You can quickly identify relevant 
            security concepts in any text.""",
        )

    def _execute_internal(
        self, task_description: str, context: Dict[str, Any]
    ) -> List[str]:
        """Execute keyword identification task

        Args:
            task_description: Description of the task
            context: Must contain 'content' key with text to analyze,
                    optionally 'keywords' list for custom keywords

        Returns:
            List of keywords found in the content

        Raises:
            ValueError: If content is not provided
        """
        content = context.get("content")
        if not content:
            raise ValueError("Content is required for keyword identification")

        keywords = context.get("keywords", [])

        logger.info("Keywords agent analyzing content (%s chars)", len(content))

        try:
            found_keywords = find_keywords_tool(content, keywords)

            if not found_keywords:
                logger.warning("No keywords found in content")
                return []

            logger.info("Found %s keywords", len(found_keywords))
            return found_keywords

        except Exception as e:
            logger.error("Keyword identification failed: %s", str(e))
            raise


# Made with Bob
