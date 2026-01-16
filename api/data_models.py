"""API data models for request and response schemas."""

from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    url: Optional[HttpUrl] = None
    keywords: Optional[List[str]] = None
    analyst_questions: Optional[List[str]] = None
    raw_text: Optional[str] = None


class FeedbackRequest(BaseModel):
    url: str
    feedback_type: str
    context: str
    value: int  # 1 for like, -1 for dislike
