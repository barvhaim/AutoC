"""LangGraph nodes that use CrewAI agents for execution"""

import os
import logging
from langgraph.graph import END
from langgraph.types import Command
from backend.pipeline.state import PipelineState
from backend.pipeline.node_types import (
    KEYWORDS_EXTRACTOR_NODE,
    IOCS_EXTRACTOR_NODE,
    MITRE_TTP_CLASSIFIER_NODE,
)
from backend.agents.agent_manager import AgentManager
from backend.agents.parser_agent import ParserAgent
from backend.agents.keywords_agent import KeywordsAgent
from backend.agents.ioc_hunter_agent import IOCHunterAgent
from backend.agents.enrichment_agent import EnrichmentAgent
from backend.agents.qna_agent import QnAAgent
from backend.agents.mitre_agent import MITREAgent

logger = logging.getLogger(__name__)

# Global agent manager instance (singleton pattern)
_agent_manager = None


def get_agent_manager() -> AgentManager:
    """Get or create the global agent manager instance"""
    global _agent_manager
    if _agent_manager is None:
        logger.info("Initializing agent manager and registering agents")
        _agent_manager = AgentManager()

        # Register all agents
        try:
            _agent_manager.register_agent("parser", ParserAgent())
            _agent_manager.register_agent("keywords", KeywordsAgent())
            _agent_manager.register_agent("ioc_hunter", IOCHunterAgent())
            _agent_manager.register_agent("enrichment", EnrichmentAgent())
            _agent_manager.register_agent("qna", QnAAgent())
            _agent_manager.register_agent("mitre", MITREAgent())
            logger.info("All agents registered successfully")
        except Exception as e:
            logger.error(f"Failed to register agents: {str(e)}")
            raise

    return _agent_manager


def html_extractor_agent_node(state: PipelineState) -> Command:
    """HTML extraction using Parser Agent

    This node uses the Parser Agent to extract textual content from URLs.
    The agent intelligently chooses between Docling and Crawl4AI parsers.
    """
    if state.get("article_textual_content"):
        logger.info("Article content already extracted, skipping HTML extraction")
        return Command(goto=KEYWORDS_EXTRACTOR_NODE)

    url = state.get("url")
    if not url:
        logger.error("No blog URL provided")
        return Command(goto=END, update={"error": "No blog URL provided"})

    try:
        logger.info(f"Using Parser Agent to extract content from {url}")
        agent_manager = get_agent_manager()

        content = agent_manager.execute_agent(
            agent_name="parser",
            task=f"Extract textual content from {url}",
            context={"url": url},
        )

        if not content:
            raise ValueError("Parser agent returned empty content")

        logger.info(f"Successfully extracted {len(content)} characters")
        return Command(
            goto="parallel_analysis", update={"article_textual_content": content}
        )

    except Exception as e:
        logger.error(f"Parser agent failed: {str(e)}")
        return Command(goto=END, update={"error": f"Failed to parse content: {str(e)}"})


def parallel_analysis_agent_node(state: PipelineState) -> Command:
    """Execute Keywords, IOC, and QnA agents in parallel

    This node runs three independent agents concurrently:
    - Keywords Agent: Identifies security keywords
    - IOC Hunter Agent: Extracts indicators of compromise
    - QnA Agent: Answers analyst questions

    This parallel execution significantly reduces total processing time.
    """
    content = state.get("article_textual_content")
    if not content:
        logger.error("No article content provided")
        return Command(goto=END, update={"error": "No article content provided"})

    settings = state.get("settings", {})

    # Prepare parallel tasks
    tasks = {
        "keywords": (
            "Find all relevant security keywords in the content",
            {"content": content, "keywords": settings.get("keywords", [])},
        ),
        "ioc_hunter": (
            "Extract all indicators of compromise from the content",
            {"content": content},
        ),
    }

    # Add QnA task if not skipped
    if os.getenv("SKIP_QNA", "false") != "true":
        # Check for batch and RAG mode settings
        batch_mode = os.getenv("QNA_BATCH_MODE", "false").lower() == "true"
        if "qna_batch_mode" in settings:
            batch_mode = str(settings.get("qna_batch_mode", False)).lower() == "true"

        rag_mode = os.getenv("QNA_RAG_MODE", "false").lower() == "true"
        if "qna_rag_mode" in settings:
            rag_mode = str(settings.get("qna_rag_mode", False)).lower() == "true"

        # Warn if both modes enabled
        if batch_mode and rag_mode:
            logger.warning("Both batch and RAG modes enabled. RAG will be disabled.")
            rag_mode = False

        tasks["qna"] = (
            "Answer analyst questions about the content",
            {
                "content": content,
                "questions": settings.get("analyst_questions", []),
                "batch_mode": batch_mode,
                "rag_mode": rag_mode,
            },
        )

    logger.info(f"Executing {len(tasks)} agents in parallel")

    try:
        # Execute agents in parallel
        agent_manager = get_agent_manager()
        results = agent_manager.execute_parallel(tasks, fail_fast=False)

        # Handle results with graceful degradation
        keywords_found = results.get("keywords", [])
        if keywords_found is None:
            logger.warning("Keywords agent failed, using empty list")
            keywords_found = []

        iocs_found = results.get("ioc_hunter", [])
        if iocs_found is None:
            logger.warning("IOC hunter agent failed, using empty list")
            iocs_found = []

        qna = results.get("qna", [])
        if qna is None:
            logger.warning("QnA agent failed, using empty list")
            qna = []

        # Log summary
        logger.info(
            f"Parallel analysis complete: "
            f"{len(keywords_found)} keywords, "
            f"{len(iocs_found)} IOCs, "
            f"{len(qna)} Q&A pairs"
        )

        # Update state and proceed to enrichment
        return Command(
            goto=IOCS_EXTRACTOR_NODE,
            update={
                "keywords_found": keywords_found,
                "iocs_found": iocs_found,
                "qna": qna,
            },
        )

    except Exception as e:
        logger.error(f"Parallel analysis failed: {str(e)}")
        return Command(
            goto=END, update={"error": f"Parallel analysis failed: {str(e)}"}
        )


def enrichment_agent_node(state: PipelineState) -> Command:
    """Enrich IOCs using Enrichment Agent

    This node enriches extracted IOCs with threat intelligence data
    from sources like VirusTotal.
    """
    iocs = state.get("iocs_found", [])

    if not iocs:
        logger.info("No IOCs to enrich, proceeding to MITRE classification")
        return Command(goto=MITRE_TTP_CLASSIFIER_NODE, update={"iocs_found": []})

    try:
        logger.info(f"Using Enrichment Agent to enrich {len(iocs)} IOCs")
        agent_manager = get_agent_manager()

        enriched_iocs = agent_manager.execute_agent(
            agent_name="enrichment",
            task="Enrich IOCs with threat intelligence data",
            context={"iocs": iocs},
        )

        if enriched_iocs is None:
            logger.warning("Enrichment failed, using original IOCs")
            enriched_iocs = iocs

        logger.info(f"Enrichment complete: {len(enriched_iocs)} IOCs")
        return Command(
            goto=MITRE_TTP_CLASSIFIER_NODE, update={"iocs_found": enriched_iocs}
        )

    except Exception as e:
        logger.error(f"Enrichment agent failed: {str(e)}")
        # Continue with unenriched IOCs
        logger.warning("Continuing with unenriched IOCs")
        return Command(goto=MITRE_TTP_CLASSIFIER_NODE)


def mitre_agent_node(state: PipelineState) -> Command:
    """Classify MITRE TTPs using MITRE Agent

    This node uses machine learning to classify content against the
    MITRE ATT&CK framework.
    """
    content = state.get("article_textual_content")
    qna = state.get("qna", [])

    if not content:
        logger.warning("No content for MITRE classification")
        return Command(goto=END, update={"mitre_ttps": None})

    try:
        logger.info("Using MITRE Agent to classify techniques")
        agent_manager = get_agent_manager()

        mitre_ttps = agent_manager.execute_agent(
            agent_name="mitre",
            task="Classify MITRE ATT&CK techniques in the content",
            context={"content": content, "qna": qna, "top_k": 3},
        )

        if mitre_ttps is None:
            logger.info("MITRE classification not configured")
        elif mitre_ttps:
            logger.info(f"Classified {len(mitre_ttps)} MITRE TTPs")
        else:
            logger.warning("No MITRE TTPs classified")

        return Command(goto=END, update={"mitre_ttps": mitre_ttps})

    except Exception as e:
        logger.error(f"MITRE agent failed: {str(e)}")
        return Command(goto=END, update={"mitre_ttps": None})
