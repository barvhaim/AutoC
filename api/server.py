import logging
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from api.data_models import AnalyzeRequest
from backend.run import run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

frontend_path = Path(__file__).parent / "../frontend/dist"

v1_router = APIRouter(prefix="/api/v1")


@v1_router.post("/analyze")
async def analyze_url(request: AnalyzeRequest):
    url = str(request.url) if request.url else None
    keywords = request.keywords if request.keywords is not None else []
    analyst_questions = (
        request.analyst_questions if request.analyst_questions is not None else []
    )
    raw_text = request.raw_text if request.raw_text else None

    try:
        res = await run_in_threadpool(
            run,
            url=url,
            keywords=keywords,
            analyst_questions=analyst_questions,
            raw_text=raw_text,
        )
        return {
            "url": url,
            "keywords_found": res.get("keywords_found"),
            "qna": res.get("qna"),
            "iocs_found": res.get("iocs_found"),
            "mitre_ttps": res.get("mitre_ttps"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@v1_router.post("/ping")
async def ping(request: AnalyzeRequest):
    url = str(request.url)
    keywords = request.keywords if request.keywords is not None else []
    analyst_questions = (
        request.analyst_questions if request.analyst_questions is not None else []
    )
    raw_text = request.raw_text if request.raw_text else None

    try:
        res = run(
            url=url,
            ping=True,
            keywords=keywords,
            analyst_questions=analyst_questions,
            raw_text=raw_text,
        )
        return {
            "url": url,
            "keywords_found": res.get("keywords_found"),
            "positive_analyst_questions": res.get("positive_analyst_questions"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


app.include_router(v1_router)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
