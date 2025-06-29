"""Given analyst question and article content, answer the question"""

from dotenv import load_dotenv
import os
import logging
from typing import List, Any, Dict
import json
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableParallel, RunnableSequence
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from backend.prompts import get_prompts
from backend.llm import get_chat_llm_client

load_dotenv()
logger = logging.getLogger(__name__)


class QnaExtractor:
    def __init__(
        self,
        article_content: str,
        analyst_questions: List[str] = None,
        batch_mode: bool = False,
    ):
        self.article_content = article_content
        self.analyst_questions = (
            analyst_questions
            if analyst_questions is not None and len(analyst_questions) > 0
            else self._load_analyst_questions()
        )
        self.batch_mode = batch_mode
        self.prompts = get_prompts()
        self.llm = self._llm()

    @staticmethod
    def _load_analyst_questions() -> List[str]:
        with open("config.json") as f:
            config = json.load(f)
            questions = config.get("analyst_questions", [])
        return questions

    @staticmethod
    def _llm() -> Any:
        model_name = os.getenv("LLM_MODEL", "meta-llama/llama-3-3-70b-instruct")
        return get_chat_llm_client(
            model_name=model_name,
            model_parameters={
                "decoding_method": "sample",
                "temperature": 0,
                "max_tokens": 350,
            },
        )

    def _answer_question(self, question: str) -> RunnableSequence:
        system_message = SystemMessagePromptTemplate.from_template(
            template=self.prompts["qna"]["system"],
            partial_variables={
                "context": self.article_content,
            },
        )
        user_message = HumanMessage(content=question)
        messages = [system_message, user_message]
        prompt = ChatPromptTemplate.from_messages(
            messages=messages,
        )
        return prompt | self.llm | StrOutputParser()

    def _batch_answer_questions(self) -> RunnableSequence:
        """Process all questions in a single model call"""
        # Format questions as numbered list
        questions_text = "\n".join(
            [f"{i+1}. {q}" for i, q in enumerate(self.analyst_questions)]
        )

        system_message = SystemMessagePromptTemplate.from_template(
            template=self.prompts["qna"]["batch_system"],
            partial_variables={
                "context": self.article_content,
                "questions": questions_text,
            },
        )

        prompt = ChatPromptTemplate.from_messages([system_message])
        return prompt | self.llm | JsonOutputParser()

    def qna_over_article(self) -> List[Dict]:
        try:
            if self.batch_mode:
                # Process all questions in a single model call
                try:
                    batch_chain = self._batch_answer_questions()
                    result = batch_chain.invoke({})

                    # Ensure we have the expected format
                    if isinstance(result, list):
                        return result
                    else:
                        # Fallback to individual mode if batch parsing fails
                        logger.warning(
                            "Batch mode failed, falling back to individual mode"
                        )
                        return self._individual_qna()
                except Exception as e:
                    logger.warning(
                        f"Batch mode failed with error {e}, falling back to individual mode"
                    )
                    return self._individual_qna()
            else:
                return self._individual_qna()
        except Exception as e:
            logger.error(f"Critical error in qna_over_article: {str(e)}")
            logger.exception("Full traceback:")
            return []

    def _individual_qna(self) -> List[Dict]:
        """Process questions individually (original behavior)"""
        try:
            qna = []
            tasks = {
                f"task{i}": self._answer_question(question)
                for i, question in enumerate(self.analyst_questions)
            }
            res = RunnableParallel(**tasks).invoke(input={})
            for i, question in enumerate(self.analyst_questions):
                qna.append(
                    {
                        "question": question,
                        "answer": res[f"task{i}"],
                    }
                )
            return qna
        except Exception as e:
            logger.error(f"Error in individual QnA processing: {str(e)}")
            logger.exception("Full traceback:")
            return []
