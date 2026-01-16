"""Main execution module for AutoC threat intelligence analysis."""

import logging
import os
from typing import Optional, Any, List
from dotenv import load_dotenv
from backend.pipeline.graph import build_graph
from backend.pipeline.agent_graph import build_agent_graph
from backend.scoring.relevancy import get_positive_qna

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(
    url: Optional[str] = None,
    ping: bool = False,
    keywords: Optional[List[str]] = None,
    analyst_questions: Optional[List[str]] = None,
    raw_text: Optional[str] = None,
) -> Any:
    # Choose graph based on configuration
    use_agents = os.getenv("AGENT_SYSTEM_ENABLED", "false").lower() == "true"

    if use_agents:
        logger.info("🤖 Using agent-based pipeline with parallel execution")
        graph = build_agent_graph()
    else:
        logger.info("📊 Using traditional sequential pipeline")
        graph = build_graph()

    inputs = {
        "url": url,
        "settings": {
            "skip_ioc_extraction": ping,
            "keywords": keywords,
            "analyst_questions": analyst_questions,
        },
        "article_textual_content": raw_text,
        "qna": [],
        "keywords_found": [],
        "iocs_found": [],
        "mitre_ttps": None,
        "error": None,
    }

    logger.info("🕵🏼‍ Analyzing url: %s", url)
    res = graph.invoke(input=inputs)

    if res.get("error"):
        logger.error("Error: %s", res.get('error'))
        raise Exception(res.get("error"))

    article = res.get("article_textual_content")
    qna = res.get("qna", [])
    keywords_found = res.get("keywords_found", [])
    iocs = res.get("iocs_found", [])
    mitre_ttps = res.get("mitre_ttps")

    if ping:
        positive_qna = get_positive_qna(qna=qna)
        return {
            "keywords_found": keywords_found,
            "positive_analyst_questions": positive_qna,
        }

    return {
        "article_textual_content": article,
        "keywords_found": keywords_found,
        "qna": qna,
        "iocs_found": [
            {"type": ioc.model_dump()["type"].name, "value": ioc.model_dump()["value"]}
            for ioc in iocs
        ],
        "mitre_ttps": mitre_ttps,
    }


if __name__ == "__main__":
    _url = "https://www.uperesia.com/how-trickbot-tricks-its-victims"
    _res = run(_url)
    logger.info("🔍Keywords found: %s", _res.get('keywords_found'))
    logger.info("📝 QnA: %s", _res.get('qna'))
    logger.info("🔍Total IoCs found: %s", len(_res.get('iocs_found')))
