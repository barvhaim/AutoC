"""IOC Hunter Agent for extracting indicators of compromise"""

import logging
from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.ioc_tools import extract_iocs_tool

logger = logging.getLogger(__name__)


class IOCHunterAgent(BaseAgent):
    """Agent responsible for extracting indicators of compromise (IOCs).

    This agent uses LLM-based extraction to identify various types of IOCs including:
    - IP addresses (IPv4, IPv6)
    - Domain names
    - URLs
    - File hashes (MD5, SHA1, SHA256)
    - Email addresses

    The agent can identify IOCs even when obfuscated or embedded in text.
    """

    def __init__(self):
        super().__init__(
            name="ioc_hunter",
            role="IOC Hunter",
            goal="Identify and extract all indicators of compromise with high accuracy",
            backstory="""You are a threat intelligence analyst with expertise in IOC
            identification and validation. You have years of experience analyzing malware 
            reports, threat intelligence feeds, and security blogs. You can spot IOCs even 
            when they are obfuscated, defanged, or embedded in complex text. You understand 
            the nuances of different IOC types and can accurately classify them.""",
        )

    def _execute_internal(
        self, task_description: str, context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Execute IOC extraction task

        Args:
            task_description: Description of the task
            context: Must contain 'content' key with text to analyze

        Returns:
            List of dictionaries containing IOC type and value
            Example: [{"type": "IPv4", "value": "192.168.1.1"}, ...]

        Raises:
            ValueError: If content is not provided
        """
        content = context.get("content")
        if not content:
            raise ValueError("Content is required for IOC extraction")

        logger.info("IOC Hunter agent analyzing content (%s chars)", len(content))

        try:
            iocs = extract_iocs_tool(content)

            if not iocs:
                logger.warning("No IOCs found in content")
                return []

            logger.info("Extracted %s IOCs", len(iocs))

            # Log IOC type distribution
            ioc_types = {}
            for ioc in iocs:
                ioc_type = ioc.get("type", "Unknown")
                ioc_types[ioc_type] = ioc_types.get(ioc_type, 0) + 1

            logger.info("IOC distribution: %s", ioc_types)

            return iocs

        except Exception as e:
            logger.error("IOC extraction failed: %s", str(e))
            raise
