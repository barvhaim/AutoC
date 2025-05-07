"""Given analyst question and article content, answer the question"""

from dotenv import load_dotenv
import os
from typing import List, Any, Dict
import json
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableParallel, RunnableSequence
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.prompts import get_prompts
from backend.llm import get_chat_llm_client

load_dotenv()


class QnaExtractor:
    def __init__(self, article_content: str, analyst_questions: List[str] = []):
        self.article_content = article_content
        self.analyst_questions = (
            analyst_questions if analyst_questions else self._load_analyst_questions()
        )
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

    def qna_over_article(self) -> List[Dict]:
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
