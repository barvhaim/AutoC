"""QnA Agent for answering analyst questions"""

import logging
from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.agents.tools.qna_tools import answer_questions_tool

logger = logging.getLogger(__name__)


class QnAAgent(BaseAgent):
    """Agent responsible for answering analyst questions about threat intelligence content.

    This agent uses LLM to answer specific questions about analyzed content.
    It supports:
    - Individual question processing (default)
    - Batch processing for efficiency
    - RAG (Retrieval-Augmented Generation) for long documents
    """

    def __init__(self):
        super().__init__(
            name="qna",
            role="Analyst Assistant",
            goal="Provide accurate answers to analyst questions about threat intelligence",
            backstory="""You are a senior threat intelligence analyst with deep expertise in
            malware analysis, threat actor profiling, and security operations. You have years 
            of experience analyzing threat reports, APT campaigns, and security incidents. You 
            can quickly extract relevant information from complex technical documents and provide 
            clear, concise answers to analyst questions. You understand the context and nuances 
            of cybersecurity terminology and can identify key details that matter for threat 
            hunting and incident response.""",
        )

    def _execute_internal(
        self, task_description: str, context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Execute question answering task

        Args:
            task_description: Description of the task
            context: Must contain:
                - 'content': Text to analyze
                - 'questions': List of questions to answer
                - 'batch_mode': (optional) Whether to use batch processing
                - 'rag_mode': (optional) Whether to use RAG for context retrieval

        Returns:
            List of dictionaries with 'question' and 'answer' keys

        Raises:
            ValueError: If content or questions are not provided
        """
        content = context.get("content")
        questions = context.get("questions", [])
        batch_mode = context.get("batch_mode", False)
        rag_mode = context.get("rag_mode", False)

        if not content:
            raise ValueError("Content is required for Q&A")

        if not questions:
            logger.warning("No questions provided, returning empty results")
            return []

        logger.info(
            f"QnA agent processing {len(questions)} questions "
            f"(batch_mode={batch_mode}, rag_mode={rag_mode})"
        )

        try:
            qna_results = answer_questions_tool(
                content=content,
                questions=questions,
                batch_mode=batch_mode,
                rag_mode=rag_mode,
            )

            if not qna_results:
                logger.warning("No Q&A results returned")
                return []

            logger.info(f"Successfully answered {len(qna_results)} questions")

            # Log sample Q&A for debugging
            if qna_results and logger.isEnabledFor(logging.DEBUG):
                sample = qna_results[0]
                logger.debug(
                    f"Sample Q&A - Q: {sample.get('question', 'N/A')[:50]}... "
                    f"A: {sample.get('answer', 'N/A')[:50]}..."
                )

            return qna_results

        except Exception as e:
            logger.error(f"Q&A processing failed: {str(e)}")
            raise


# Made with Bob
