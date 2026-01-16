"""MITRE ATT&CK classification tools"""

import logging
import os
from typing import Dict, List, Optional

from backend.extractors.mitre_ttp_classifier_extractor import (
    MitreTTPClassifierExtractor,
)

logger = logging.getLogger(__name__)


def classify_mitre_ttps_tool(
    content: str, qna: Optional[List[Dict[str, str]]] = None, top_k: int = 3
) -> Optional[List[Dict]]:
    """Classify content against the MITRE ATT&CK framework.

    This tool uses a machine learning model to identify relevant MITRE ATT&CK
    techniques, tactics, and procedures (TTPs) mentioned in the content. It can
    analyze both the main content and Q&A results for better classification.

    The tool returns the top-K most relevant techniques with confidence scores
    and enriched metadata including:
    - Technique ID and name
    - Tactic information
    - Description
    - Detection methods
    - Mitigation strategies

    Args:
        content: The textual content to classify
        qna: Optional Q&A results to enhance classification accuracy
        top_k: Number of top techniques to return (default: 3)

    Returns:
        List of dictionaries containing MITRE ATT&CK technique information,
        or None if MITRE classification is not configured
    """
    try:
        model_path = os.getenv("DETECT_MITRE_TTPS_MODEL_PATH")
        if not model_path:
            logger.info("MITRE TTP classification not configured (no model path)")
            return None

        logger.info("Classifying content for MITRE TTPs (top_k=%s)", top_k)

        extractor = MitreTTPClassifierExtractor(
            article_content=content, model_repo=model_path, qna=qna or [], top_k=top_k
        )

        mitre_ttps = extractor.classify()

        if mitre_ttps:
            logger.info("Classified %s MITRE TTPs", len(mitre_ttps))
        else:
            logger.warning("No MITRE TTPs classified")

        return mitre_ttps

    except Exception as e:
        logger.error("MITRE TTP classification failed: %s", str(e))
        raise
