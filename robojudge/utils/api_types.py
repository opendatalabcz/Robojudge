import datetime
from typing import Optional

from pydantic import BaseModel, Field

from robojudge.utils.internal_types import ScrapingFilters, Case


class CaseSearchRequestFilters(BaseModel):
    publication_date_from: Optional[float] = Field()
    publication_date_to: Optional[float] = Field()
    sentence_date_from: Optional[float] = Field()
    sentence_date_to: Optional[float] = Field()


class CaseSearchRequest(BaseModel):
    query_text: str = Field(
        description="Any string of text which should have similar cases in the DB. Longer texts have more accurate results."
    )
    filters: Optional[CaseSearchRequestFilters]
    sentence_date_from: Optional[datetime.datetime]
    sentence_date_to: Optional[datetime.datetime]
    court: Optional[str]
    page_size: Optional[int] = Field(
        default=3,
        description="The number of results to return in a single response.",
    )
    current_page: Optional[int] = Field(
        default=0, description="Which page of the results to return.")
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
    max_page: int = 0
