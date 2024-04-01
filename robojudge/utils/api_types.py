import datetime
from typing import Optional

from pydantic import BaseModel, Field

from robojudge.utils.internal_types import ScrapingFilters, Case, ScrapingJobStatus

# TODO: change from timestamps


# TODO: update desc and type
class CaseSearchRequestFilters(BaseModel):
    publication_date_from: Optional[float] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    publication_date_to: Optional[float] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    sentence_date_from: Optional[float] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    sentence_date_to: Optional[float] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )


class CaseSearchRequest(BaseModel):
    query_text: str = Field(
        description="Any string of text which should have similar cases in the DB. Longer texts have more accurate results.",
        example="Soud řešil rozvod manželství, protože každý z manželů měl jiného partnera a nechtěli spolu zůstat.",
        max_length=20000,
        min_length=20,
    )
    filters: Optional[CaseSearchRequestFilters]
    page_size: Optional[int] = Field(
        default=3,
        description="The number of results to return in a single response.",
    )
    current_page: Optional[int] = Field(
        default=0, description="Which page of the results to return."
    )
    generate_summaries: Optional[bool] = Field(
        default=False,
        description="Whether to generate any new summaries. In case the case already has a summary in DB, it will return that.",
    )


class CaseQuestionRequest(BaseModel):
    question: str = Field(
        description="Question to the LLM about a ruling.",
        example="Kolik bylo v případu žalobců?",
        max_length=250,
    )


class CaseQuestionResponse(BaseModel):
    answer: str = Field(description="The LLM's answer to a question (request).")


class FetchCasesRequest(BaseModel):
    limit: Optional[int] = Field(
        default=1000,
        le=1000,
        description="Maximum number of rulings to scrape based on the filters.",
    )
    filters: ScrapingFilters


class FetchCasesResponse(BaseModel):
    token: str = Field(
        description="Unique identifier of the scraping job used for polling the API."
    )


class FetchCasesStatusResponse(BaseModel):
    status: ScrapingJobStatus = Field(
        description="The current status of the fetch job."
    )
    content: Optional[list[Case]] = Field(
        description="Rulings that were scraped (gradually added as more are scraped)."
    )


class SearchCasesResponse(BaseModel):
    cases: list[Case] = Field(
        default=[], description="Found rulings based on the query text."
    )
    relevance: bool = Field(
        default=True,
        description="Becomes false if the query text was irrelevant to the DB contents (judged by LLM).",
    )
    reasoning: str = Field(
        default="",
        description="In case of an irrelevant query text, the LLM sends back an explanation why.",
    )
    max_page: int = Field(default=0, description="Used for frontend pagination.")
