from typing import Annotated, Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel

from server.db.chroma_db import embedding_db

class CaseSearchRequest(BaseModel):
    query_text: str
    limit: Optional[int] = 5
    included_fields: Optional[list[str]] = ['documents', 'metadatas']

router = APIRouter(prefix='/cases')

# TODO: authentication for this method or remove
@router.get('/all')
async def get_all_cases():
    return embedding_db.get_all_cases()


@router.post('/search')
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())

    return cases
