import os
from dotenv import load_dotenv
import logging
from langgraph.graph import END
from langgraph.types import Command
from backend.pipeline.state import PipelineState
from backend.pipeline.node_types import (
    KEYWORDS_EXTRACTOR_NODE,
    QNA_EXTRACTOR_NODE,
    IOCS_EXTRACTOR_NODE,
    MITRE_CLASSIFIER_NODE,
)
from backend.parsers.html_parser import HTMLParser
from backend.extractors.keywords_extractor import KeywordsExtractor
from backend.extractors.qna_extractor import QnaExtractor
from backend.extractors.iocs_extractor import IOCsExtractor
from backend.enrichment.enrich_iocs import EnrichIOCs
from backend.extractors.mitre_classifier_extractor import mitreClassifierExtractor

load_dotenv()
logger = logging.getLogger(__name__)


def html_extractor_node(state: PipelineState) -> Command:
    url = state.get("url")
    if not url:
        logger.error("No blog URL provided")
        return Command(goto=END, update={"error": "No blog URL provided"})

    logger.info(f"Extracting content from {url}")
    parser = HTMLParser(url=url, use_ocr=os.getenv("ANALYZE_BLOG_IMAGES", 'false') == 'true')
    article_textual_content = parser.get_textual_content()

    return Command(
        goto=KEYWORDS_EXTRACTOR_NODE,
        update={"article_textual_content": article_textual_content},
    )


def keywords_extractor_node(state: PipelineState) -> Command:
    article_textual_content = state.get("article_textual_content")

    if not article_textual_content:
        logger.error("No article content provided")
        return Command(goto=END, update={"error": "No article content provided"})
    
    settings = state.get("settings", {})
    keywords = settings.get("keywords")
    logger.info(f"Extracting keywords from article content")
    extractor = KeywordsExtractor(article_content=article_textual_content, keywords=keywords)
    keywords_found = extractor.find_keywords_in_text()

    if not keywords_found:
        logger.error("No keywords found in article content")
        return Command(
            goto=END,
            update={"keywords_found": []},
        )

    return Command(
        goto=QNA_EXTRACTOR_NODE,
        update={"keywords_found": keywords_found},
    )


def qna_extractor_node(state: PipelineState) -> Command:
    article_textual_content = state.get("article_textual_content")

    if not article_textual_content:
        logger.error("No article content provided")
        return Command(goto=END, update={"error": "No article content provided"})

    if os.getenv("SKIP_QNA", "false") == "true":
        return Command(
            goto=IOCS_EXTRACTOR_NODE,
        )
    
    settings = state.get("settings", {})
    analyst_questions = settings.get("analyst_questions")

    logger.info(f"QnA extraction from article content")
    extractor = QnaExtractor(article_content=article_textual_content, analyst_questions=analyst_questions)
    qna = extractor.qna_over_article()

    if not qna:
        logger.error("Failed to extract QnA from article content")
        return Command(
            goto=END, update={"error": "Failed to extract QnA from article content"}
        )

    return Command(
        goto=IOCS_EXTRACTOR_NODE,
        update={"qna": qna},
    )


def iocs_extractor_node(state: PipelineState) -> Command:
    settings = state.get("settings", {})
    if settings.get("skip_ioc_extraction", False):
        return Command(
            goto=END,
            update={"iocs_found": []},
        )

    article_textual_content = state.get("article_textual_content")
    if not article_textual_content:
        logger.error("No article content provided")
        return Command(goto=END, update={"error": "No article content provided"})

    logger.info(f"Extracting IOCs from article content")
    extractor = IOCsExtractor(article_content=article_textual_content)

    iocs = extractor.extract_iocs_from_text()
    iocs_enrichment = EnrichIOCs(iocs=iocs)
    enriched_iocs = iocs_enrichment.enrich_iocs()

    return Command(
        goto=MITRE_CLASSIFIER_NODE,
        update={"iocs_found": enriched_iocs},
    )

def mitre_ttp_classifier_node(state: PipelineState) -> Command:
    model_path = os.getenv("API_MITRE_TTP")
    if not model_path:
        return Command(
            goto=END,
           update={"mitre_ttp": None},
        )
    article_textual_content = state.get("article_textual_content")
    qna = state.get("qna", [])
    if not article_textual_content:
        return Command(goto=END, update={"mitre_ttp": []})
    try:
        extractor = mitreClassifierExtractor(
            article_content=article_textual_content,
            model_repo=model_path,
            qna=qna
        )
        mitre_ttp = extractor.classify()

    except Exception as e:
        logger.error(e)
        mitre_ttp = None

    return Command(
        goto=END,
        update={"mitre_ttp": mitre_ttp},
    )

