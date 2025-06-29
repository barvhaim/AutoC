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
    MITRE_TTP_CLASSIFIER_NODE,
)
from backend.parsers.html_parser import HtmlParser
from backend.parsers.crawl4ai_html_parser import Crawl4AiHtmlParser
from backend.extractors.keywords_extractor import KeywordsExtractor
from backend.extractors.qna_extractor import QnaExtractor
from backend.extractors.iocs_extractor import IOCsExtractor
from backend.enrichment.enrich_iocs import EnrichIOCs
from backend.extractors.mitre_ttp_classifier_extractor import (
    MitreTTPClassifierExtractor,
)

load_dotenv()
logger = logging.getLogger(__name__)


def html_extractor_node(state: PipelineState) -> Command:
    if state.get("article_textual_content"):
        logger.info("Article content already extracted, skipping HTML extraction")
        return Command(goto=KEYWORDS_EXTRACTOR_NODE)

    url = state.get("url")
    if not url:
        logger.error("No blog URL provided")
        return Command(goto=END, update={"error": "No blog URL provided"})

    use_crawl4ai_parser = (
        os.getenv("USE_CRAWL4AI_HEADLESS_BROWSER_HTML_PARSER", "false").lower()
        == "true"
    )
    if use_crawl4ai_parser:
        logger.info(f"Extracting content from {url} using Crawl4AI parser")
        parser = Crawl4AiHtmlParser(
            url=url, use_ocr=os.getenv("ANALYZE_BLOG_IMAGES", "false").lower() == "true"
        )
    else:
        logger.info(f"Extracting content from {url} using Docling")
        parser = HtmlParser(
            url=url, use_ocr=os.getenv("ANALYZE_BLOG_IMAGES", "false") == "true"
        )
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
    extractor = KeywordsExtractor(
        article_content=article_textual_content, keywords=keywords
    )
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

    # Check for batch mode setting from environment or settings
    batch_mode = os.getenv("QNA_BATCH_MODE", "false").lower() == "true"
    if "qna_batch_mode" in settings:
        batch_mode = str(settings.get("qna_batch_mode", False)).lower() == "true"

    # Check for RAG mode setting from environment or settings
    rag_mode = os.getenv("QNA_RAG_MODE", "false").lower() == "true"
    if "qna_rag_mode" in settings:
        rag_mode = str(settings.get("qna_rag_mode", False)).lower() == "true"

    # Warn if both batch and RAG modes are enabled
    if batch_mode and rag_mode:
        logger.warning(
            "Both batch mode and RAG mode are enabled. RAG mode will be disabled in favor of batch mode."
        )
        rag_mode = False

    logger.info(
        f"QnA extraction from article content (batch_mode={batch_mode}, rag_mode={rag_mode})"
    )

    try:
        extractor = QnaExtractor(
            article_content=article_textual_content,
            analyst_questions=analyst_questions,
            batch_mode=batch_mode,
            rag_mode=rag_mode,
        )
        qna = extractor.qna_over_article()

        # Clean up RAG resources if used
        if rag_mode:
            try:
                extractor.cleanup_rag()
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup RAG resources: {cleanup_error}")

        if not qna:
            logger.error("Failed to extract QnA from article content")
            return Command(
                goto=END, update={"error": "Failed to extract QnA from article content"}
            )
    except Exception as e:
        logger.error(f"Exception in QnA extraction: {str(e)}")
        logger.exception("Full traceback:")
        return Command(
            goto=END,
            update={"error": f"Failed to extract QnA from article content: {str(e)}"},
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
        goto=MITRE_TTP_CLASSIFIER_NODE,
        update={"iocs_found": enriched_iocs},
    )


def mitre_ttp_classifier_node(state: PipelineState) -> Command:
    model_path = os.getenv("DETECT_MITRE_TTPS_MODEL_PATH")
    top_k = 3  # Limit to top 3 MITRE TTPs
    mitre_ttps = None
    if not model_path:
        return Command(
            goto=END,
            update={"mitre_ttps": None},
        )
    article_textual_content = state.get("article_textual_content")
    qna = state.get("qna", [])
    if not article_textual_content:
        logger.error("No content provided")
        return Command(goto=END, update={"mitre_ttps": []})
    try:
        logger.info("Classifying content for MITRE TTPS")
        extractor = MitreTTPClassifierExtractor(
            article_content=article_textual_content,
            model_repo=model_path,
            qna=qna,
            top_k=top_k,
        )
        mitre_ttps = extractor.classify()

    except Exception as e:
        logger.error(f"Failed to classify content for MITRE TTPS: {e}")

    return Command(
        goto=END,
        update={"mitre_ttps": mitre_ttps},
    )
