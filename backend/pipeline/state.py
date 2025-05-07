from typing import Optional, List, Dict
from typing_extensions import TypedDict
from backend.data_model.ioc import IOC


class PipelineState(TypedDict):
    url: str
    settings: Dict
    article_textual_content: Optional[str]
    qna: List[Dict]
    keywords_found: List[str]
    iocs_found: List[IOC]
    mitre_ttp: List[Dict]
    error: Optional[str]
   