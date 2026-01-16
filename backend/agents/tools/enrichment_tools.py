"""Enrichment tools for IOC threat intelligence"""

import logging
from typing import Dict, List

from backend.data_model.ioc import IOC, IOCType
from backend.enrichment.enrich_iocs import EnrichIOCs

logger = logging.getLogger(__name__)


def enrich_iocs_tool(iocs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Enrich IOCs with external threat intelligence data.

    This tool enriches indicators of compromise with additional information from
    threat intelligence sources like VirusTotal. It can:
    - Convert MD5 hashes to SHA256
    - Add threat intelligence context
    - Validate and normalize IOC formats

    Args:
        iocs: List of IOC dictionaries with 'type' and 'value' keys
              Example: [{"type": "MD5", "value": "abc123..."}, ...]

    Returns:
        List of enriched IOC dictionaries with additional threat intelligence
    """
    try:
        logger.info(f"Enriching {len(iocs)} IOCs")

        # Convert dictionaries to IOC objects
        ioc_objects = []
        for ioc_dict in iocs:
            try:
                ioc_type = IOCType[ioc_dict["type"]]
                ioc_objects.append(IOC(type=ioc_type, value=ioc_dict["value"]))
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid IOC: {ioc_dict} - {str(e)}")
                continue

        # Enrich IOCs
        enricher = EnrichIOCs(iocs=ioc_objects)
        enriched = enricher.enrich_iocs()

        # Convert back to dictionaries
        enriched_dicts = [
            {"type": ioc.type.name, "value": ioc.value} for ioc in enriched
        ]

        logger.info(f"Successfully enriched {len(enriched_dicts)} IOCs")
        return enriched_dicts
    except Exception as e:
        logger.error(f"IOC enrichment failed: {str(e)}")
        raise


# Made with Bob
