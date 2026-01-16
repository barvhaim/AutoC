"""IOC extraction tools"""

import logging
from typing import Dict, List

from backend.extractors.iocs_extractor import IOCsExtractor

logger = logging.getLogger(__name__)


def extract_iocs_tool(content: str) -> List[Dict[str, str]]:
    """Extract all indicators of compromise (IOCs) from the given content.

    This tool uses LLM-based extraction to identify various types of IOCs including:
    - IP addresses (IPv4, IPv6)
    - Domain names
    - URLs
    - File hashes (MD5, SHA1, SHA256)
    - Email addresses

    The tool intelligently identifies IOCs even when they are obfuscated or
    embedded in text.

    Args:
        content: The textual content to extract IOCs from

    Returns:
        List of dictionaries containing IOC type and value
        Example: [{"type": "IPv4", "value": "192.168.1.1"}, ...]
    """
    try:
        logger.info(f"Extracting IOCs from content ({len(content)} chars)")
        extractor = IOCsExtractor(article_content=content)
        iocs = extractor.extract_iocs_from_text()

        # Convert IOC objects to dictionaries
        ioc_dicts = [{"type": ioc.type.name, "value": ioc.value} for ioc in iocs]

        logger.info(f"Extracted {len(ioc_dicts)} IOCs")
        return ioc_dicts
    except Exception as e:
        logger.error(f"IOC extraction failed: {str(e)}")
        raise


# Made with Bob
