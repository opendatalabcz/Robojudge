from typing import Annotated

from fastapi import APIRouter, Depends, Body

from server.db.chroma_db import embedding_db
from server.model.gpt import OpenAIPrompter

router = APIRouter(prefix='/case-query')


@router.post('/')
async def get_summaries(case_description: Annotated[str, Body()]):
    cases = embedding_db.query_documents(case_description)
    # summaries = []
    # for case in cases:
    #     summaries.append(OpenAIPrompter.summarize_case(case.text))
    return cases
