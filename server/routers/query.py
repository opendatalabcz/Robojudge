from typing import Annotated

from fastapi import APIRouter, Depends

from server.db.vector_db import DB
from server.model.gpt import OpenAIPrompter

router = APIRouter(prefix='/case-query')


@router.post('/')
async def get_summaries(case_description: str, vector_db: Annotated[DB, Depends()]):
    # cases = vector_db.query_documents(case_description)
    summaries = []
    for case in cases:
        summaries.append(OpenAIPrompter.summarize_case(case))

    return
