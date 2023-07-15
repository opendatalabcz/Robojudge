from typing import Annotated

from fastapi import APIRouter, Body

from server.db.chroma_db import embedding_db
from server.model.gpt import OpenAIPrompter

router = APIRouter(prefix='/summary')

@router.post('/')
async def search_cases(case_description: Annotated[str, Body()]):
    cases = embedding_db.find_case_chunks_by_text(case_description)
    # summaries = []
    # for case in cases:
    #     summaries.append(OpenAIPrompter.summarize_case(case.text))
    return cases
