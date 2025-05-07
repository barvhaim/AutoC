from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    keywords: Optional[List[str]] = None
    analyst_questions: Optional[List[str]] = None
