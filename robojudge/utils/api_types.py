from typing import Optional

from pydantic import BaseModel


class CaseSearchRequest(BaseModel):
    query_text: str
    limit: Optional[int] = 3
    included_fields: Optional[list[str]] = ["documents", "metadatas"]


class CaseQuestionRequest(BaseModel):
    question: str
    case_id: str
