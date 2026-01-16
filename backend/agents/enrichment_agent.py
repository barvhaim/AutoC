"""Enrichment Agent for IOC threat intelligence enrichment"""

import logging
from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.enrichment_tools import enrich_iocs_tool

logger = logging.getLogger(__name__)


class EnrichmentAgent(BaseAgent):
    """Agent responsible for enriching IOCs with external threat intelligence.

    This agent enriches indicators of compromise with additional information from
    threat intelligence sources like VirusTotal. It can:
    - Convert MD5 hashes to SHA256
    - Add threat intelligence context
    - Validate and normalize IOC formats
    - Handle API rate limits gracefully
    """

    def __init__(self):
        super().__init__(
            name="enrichment",
            role="Threat Intelligence Enricher",
            goal="Enrich IOCs with external threat intelligence data",
            backstory="""You are a threat intelligence analyst with access to premium threat
            feeds and intelligence sources. You specialize in enriching raw indicators with 
            contextual information, reputation data, and historical intelligence. You understand 
            the importance of accurate IOC classification and can handle various data sources 
            including VirusTotal, threat feeds, and OSINT sources. You are skilled at managing 
            API rate limits and caching strategies.""",
        )

    def _execute_internal(
        self, task_description: str, context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Execute IOC enrichment task

        Args:
            task_description: Description of the task
            context: Must contain 'iocs' key with list of IOC dictionaries
                    Each IOC should have 'type' and 'value' keys

        Returns:
            List of enriched IOC dictionaries

        Raises:
            ValueError: If IOCs are not provided
        """
        iocs = context.get("iocs")
        if not iocs:
            raise ValueError("IOCs are required for enrichment")

        if not isinstance(iocs, list):
            raise ValueError("IOCs must be a list")

        logger.info("Enrichment agent processing %s IOCs", len(iocs))

        try:
            enriched_iocs = enrich_iocs_tool(iocs)

            if not enriched_iocs:
                logger.warning("Enrichment returned no IOCs")
                return []

            # Log enrichment statistics
            original_count = len(iocs)
            enriched_count = len(enriched_iocs)

            if enriched_count < original_count:
                logger.warning(
                    "Some IOCs were filtered during enrichment (%s -> %s)",
                    original_count, enriched_count
                )

            logger.info("Successfully enriched %s IOCs", enriched_count)
            return enriched_iocs

        except Exception as e:
            logger.error("IOC enrichment failed: %s", str(e))
            # Return original IOCs if enrichment fails
            logger.warning("Returning original IOCs without enrichment")
            return iocs


# Made with Bob
