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
        logger.info("Enriching %d IOCs", len(iocs))

        # Convert dictionaries to IOC objects
        ioc_objects = []
        for ioc_dict in iocs:
            try:
                # Handle both enum name (e.g., "URL") and enum value (e.g., "Domain or URL")
                ioc_type_str = ioc_dict["type"]

                # Try to get by name first
                try:
                    ioc_type = IOCType[ioc_type_str]
                except KeyError as exc:
                    # If that fails, try to find by value
                    ioc_type = None
                    for enum_member in IOCType:
                        if enum_member.value == ioc_type_str:
                            ioc_type = enum_member
                            break

                    if ioc_type is None:
                        raise ValueError(f"Unknown IOC type: {ioc_type_str}") from exc

                ioc_objects.append(IOC(type=ioc_type, value=ioc_dict["value"]))
            except (KeyError, ValueError) as e:
                logger.warning("Skipping invalid IOC: %s - %s", ioc_dict, str(e))
                continue

        logger.info("Converted %d IOC dictionaries to objects", len(ioc_objects))

        # Enrich IOCs
        enricher = EnrichIOCs(iocs=ioc_objects)
        enriched = enricher.enrich_iocs()

        # Convert back to dictionaries
        enriched_dicts = []
        for ioc in enriched:
            # Handle both enum and string types
            ioc_type = ioc.type.name if hasattr(ioc.type, "name") else str(ioc.type)
            enriched_dicts.append({"type": ioc_type, "value": ioc.value})

        logger.info("Successfully enriched %d IOCs", len(enriched_dicts))
        return enriched_dicts
    except Exception as e:
        logger.error("IOC enrichment failed: %s", str(e))
        raise
