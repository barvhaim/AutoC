"""MITRE ATT&CK Agent for threat technique classification"""

import logging
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.mitre_tools import classify_mitre_ttps_tool

logger = logging.getLogger(__name__)


class MITREAgent(BaseAgent):
    """Agent responsible for classifying content against the MITRE ATT&CK framework.

    This agent uses machine learning to identify relevant MITRE ATT&CK techniques,
    tactics, and procedures (TTPs) mentioned in threat intelligence content.
    It provides enriched metadata including detection methods and mitigation strategies.
    """

    def __init__(self):
        super().__init__(
            name="mitre",
            role="MITRE ATT&CK Classifier",
            goal="Accurately classify threat techniques using MITRE ATT&CK framework",
            backstory="""You are a threat intelligence analyst specialized in the MITRE ATT&CK
            framework with deep knowledge of adversary tactics, techniques, and procedures. You 
            have extensive experience mapping threat actor behaviors to the ATT&CK matrix and 
            understanding the relationships between different techniques. You can identify subtle 
            indicators of specific TTPs in threat reports and provide comprehensive context about 
            attack patterns, detection strategies, and defensive measures.""",
        )

    def _execute_internal(
        self, task_description: str, context: Dict[str, Any]
    ) -> Optional[List[Dict]]:
        """Execute MITRE ATT&CK classification task

        Args:
            task_description: Description of the task
            context: Must contain:
                - 'content': Text to classify
                - 'qna': (optional) Q&A results for enhanced classification
                - 'top_k': (optional) Number of top techniques to return (default: 3)

        Returns:
            List of dictionaries containing MITRE ATT&CK technique information,
            or None if classification is not configured

        Raises:
            ValueError: If content is not provided
        """
        content = context.get("content")
        if not content:
            raise ValueError("Content is required for MITRE classification")

        qna = context.get("qna", [])
        top_k = context.get("top_k", 3)

        logger.info(
            f"MITRE agent classifying content "
            f"(top_k={top_k}, with_qna={len(qna) > 0})"
        )

        try:
            mitre_ttps = classify_mitre_ttps_tool(
                content=content, qna=qna if qna else None, top_k=top_k
            )

            if mitre_ttps is None:
                logger.info("MITRE classification not configured (no model path)")
                return None

            if not mitre_ttps:
                logger.warning("No MITRE TTPs classified")
                return []

            logger.info(f"Classified {len(mitre_ttps)} MITRE TTPs")

            # Log classified techniques for debugging
            if logger.isEnabledFor(logging.DEBUG):
                for ttp in mitre_ttps[:3]:  # Log first 3
                    technique_id = ttp.get("technique_id", "Unknown")
                    technique_name = ttp.get("technique_name", "Unknown")
                    logger.debug(f"Classified TTP: {technique_id} - {technique_name}")

            return mitre_ttps

        except Exception as e:
            logger.error(f"MITRE classification failed: {str(e)}")
            raise


# Made with Bob
