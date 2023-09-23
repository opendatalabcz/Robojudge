import asyncio
from threading import Thread

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse, JSONResponse

from robojudge.tasks.case_scraping import fetch_new_cases
from robojudge.utils.logger import logging
from robojudge.utils.api_types import CaseQuestionRequest, CaseSearchRequest
from robojudge.db.chroma_db import embedding_db
from robojudge.db.mongo_db import document_db
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("/all")
async def get_all_cases():
    return embedding_db.get_all_cases()


@router.post("/search")
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())

    return cases


@router.post("/question")
async def search_cases(request: CaseQuestionRequest):
    case = document_db.collection.find_one({"case_id": request.case_id})

    answer = await CaseQuestionAnswerer.answer_question(request.question, case['reasoning'])

    return JSONResponse({'answer': answer})


@router.post("/fetch-cases")
async def fetch_cases():
    logger.info("Triggering case scraping based on an API request.")
    Thread(target=lambda: asyncio.run(fetch_new_cases())).start()
    return PlainTextResponse("ok", 202)
