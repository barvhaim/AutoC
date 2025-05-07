import logging
from typing import Optional, Any, List
from dotenv import load_dotenv
from backend.pipeline.graph import build_graph
from backend.scoring.relevancy import get_positive_qna

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(url: Optional[str] = None, ping: bool = False, keywords: List[str]=[], analyst_questions: List[str]=[]) -> Any:
    graph = build_graph()
    inputs = {
        "url": url,
        "settings": {
                        "skip_ioc_extraction": ping,
                        "keywords": keywords,
                        "analyst_questions": analyst_questions
                    },
        "article_textual_content": None,
        "qna": [],
        "keywords_found": [],
        "iocs_found": [],
        "mitre_ttp": [],
        "error": None,
    }

    logger.info(f"🕵🏼‍ Analyzing url: {url}")
    res = graph.invoke(input=inputs)

    if res.get("error"):
        logger.error(f"Error: {res.get('error')}")
        raise Exception(res.get("error"))

    article = res.get("article_textual_content")
    qna = res.get("qna", [])
    keywords_found = res.get("keywords_found", [])
    iocs = res.get("iocs_found", [])

    if ping:
        positive_qna = get_positive_qna(qna=qna)
        return {"keywords_found": keywords_found, "positive_analyst_questions": positive_qna}
    mitre_ttp = res.get("mitre_ttp", [])

    return {
        "article_textual_content": article,
        "keywords_found": keywords_found,
        "qna": qna,
        "iocs_found": [
            {"type": ioc.model_dump()["type"].name, "value": ioc.model_dump()["value"]}
            for ioc in iocs
        ],
        "mitre_ttp": mitre_ttp,
    }


if __name__ == "__main__":
    _url = "https://securityintelligence.com/posts/gozi-strikes-again-targeting-banks-cryptocurrency-and-more"
    _res = run(_url)
    logger.info(f"🔍Keywords found: {_res.get('keywords_found')}")
    logger.info(f"📝 QnA: {_res.get('qna')}")
    logger.info(f"🔍Total IoCs found: {len(_res.get('iocs_found'))}")
