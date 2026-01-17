"""Tools for AutoC agents"""

from backend.agents.tools.parser_tools import docling_parser_tool, crawl4ai_parser_tool
from backend.agents.tools.keywords_tools import find_keywords_tool
from backend.agents.tools.ioc_tools import extract_iocs_tool
from backend.agents.tools.enrichment_tools import enrich_iocs_tool
from backend.agents.tools.qna_tools import answer_questions_tool
from backend.agents.tools.mitre_tools import classify_mitre_ttps_tool

__all__ = [
    "docling_parser_tool",
    "crawl4ai_parser_tool",
    "find_keywords_tool",
    "extract_iocs_tool",
    "enrich_iocs_tool",
    "answer_questions_tool",
    "classify_mitre_ttps_tool",
]
