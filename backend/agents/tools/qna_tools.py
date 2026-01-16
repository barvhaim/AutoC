"""Question and Answer tools"""

import logging
from typing import Dict, List

from backend.extractors.qna_extractor import QnaExtractor

logger = logging.getLogger(__name__)


def answer_questions_tool(
    content: str, questions: List[str], batch_mode: bool = False, rag_mode: bool = False
) -> List[Dict[str, str]]:
    """Answer analyst questions about threat intelligence content.

    This tool uses LLM to answer specific questions about the analyzed content.
    It supports two modes:
    - Individual mode: Each question is processed separately (default)
    - Batch mode: All questions processed together for efficiency

    It also supports RAG (Retrieval-Augmented Generation) mode for long documents,
    which uses semantic search to find relevant content chunks before answering.

    Args:
        content: The textual content to analyze
        questions: List of questions to answer
        batch_mode: If True, process all questions in one LLM call
        rag_mode: If True, use RAG for better context retrieval (requires Milvus)

    Returns:
        List of dictionaries with 'question' and 'answer' keys
        Example: [{"question": "What malware?", "answer": "TrickBot"}, ...]
    """
    try:
        logger.info(
            f"Answering {len(questions)} questions "
            f"(batch_mode={batch_mode}, rag_mode={rag_mode})"
        )

        extractor = QnaExtractor(
            article_content=content,
            analyst_questions=questions,
            batch_mode=batch_mode,
            rag_mode=rag_mode,
        )

        qna_results = extractor.qna_over_article()

        if not qna_results:
            logger.warning("No Q&A results returned")
            return []

        logger.info(f"Successfully answered {len(qna_results)} questions")
        return qna_results

    except Exception as e:
        logger.error(f"Q&A extraction failed: {str(e)}")
        raise


# Made with Bob
