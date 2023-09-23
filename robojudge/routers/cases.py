from typing import Annotated, Optional
import asyncio

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from multiprocessing import Process

from robojudge.tasks.case_scraping import fetch_new_cases
from robojudge.utils.logger import logging
from robojudge.db.chroma_db import embedding_db

logger = logging.getLogger(__name__)

class CaseSearchRequest(BaseModel):
    query_text: str
    limit: Optional[int] = 3
    included_fields: Optional[list[str]] = ['documents', 'metadatas']

router = APIRouter(prefix='/cases', tags=['Cases'])

@router.get('/all')
async def get_all_cases():
    return embedding_db.get_all_cases()


@router.post('/search')
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())

    return cases

@router.post('/fetch-cases')
async def fetch_cases():
    logger.info('Triggering case scraping based on an API request.')
    Process(target=lambda: asyncio.run(fetch_new_cases())).start()
    return PlainTextResponse('ok', 202)
