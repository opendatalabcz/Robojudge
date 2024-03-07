from typing import Optional

from pydantic import BaseModel, Field

from robojudge.utils.internal_types import ScrapingFilters, Case


class CaseSearchRequest(BaseModel):
    query_text: str = Field(
        description="Any string of text which should have similar cases in the DB. Longer texts have more accurate results."
    )
    limit: Optional[int] = Field(
        default=3,
        description="The number of results may be lower if the most similar text chunks belong to the same court case(s).",
    )
    generate_summaries: Optional[bool] = Field(
        default=False,
        description="Whether to generate any new summaries. In case the case already has a summary in DB, it will return that.",
    )


class CaseQuestionRequest(BaseModel):
    question: str


class CaseQuestionResponse(BaseModel):
    answer: str


class FetchCasesRequest(BaseModel):
    limit: Optional[int] = None
    filters: ScrapingFilters


class FetchCasesStatusResponse(BaseModel):
    status: str
    content: Optional[list[Case]] = None


class SearchCasesResponse(BaseModel):
    cases: list[Case] = []
    relevance: bool = True
    reasoning: str = ''
