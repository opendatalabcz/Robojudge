from typing import Annotated

from fastapi import APIRouter, Body

from server.db.chroma_db import embedding_db
from server.model.gpt import OpenAIPrompter
from server.routers.cases import CaseSearchRequest

router = APIRouter(prefix='/summary')


@router.post('/search')
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())
    case_ids = set(case.case_id for case in cases)

    # Find all chunks for the case_ids and put them together to create the original whole reasoning
    case_reasonings: list[list[str]] = []
    for case_id in case_ids:
        case_chunks = embedding_db.collection.get(ids=[], where={"case_id": {
            "$eq": case_id
        }})
        case_reasonings.append(case_chunks['documents'])

    case_summaries = []
    for reasoning in case_reasonings:
        # Use the beginning and end of the reasoning for summary
        text_excerpt = '\n'.join([*reasoning[:2], *reasoning[-2:]])
        case_summaries.append(OpenAIPrompter.summarize_case(text_excerpt))

    return case_summaries
