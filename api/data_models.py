from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    url: Optional[HttpUrl] = None
    keywords: Optional[List[str]] = None
    analyst_questions: Optional[List[str]] = None
    raw_text: Optional[str] = None
