from typing import Optional

from pydantic import BaseModel, Field

from robojudge.utils.internal_types import Ruling


class RulingSearchRequestFilters(BaseModel):
    publication_date_from: Optional[str] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    publication_date_to: Optional[str] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    sentence_date_from: Optional[str] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )
    sentence_date_to: Optional[str] = Field(
        description="String date in the 'YYYY-MM-DD' format. Publication means when the ruling was uploaded to the justice.cz website",
    )


class RulingSearchRequest(BaseModel):
    query_text: str = Field(
        description="Any string of text which should have similar rulings in the DB. Longer texts have more accurate results.",
        example="Soud řešil rozvod manželství, protože každý z manželů měl jiného partnera a nechtěli spolu zůstat.",
        max_length=20000,
        min_length=20,
    )
    filters: Optional[RulingSearchRequestFilters]
    page_size: Optional[int] = Field(
        default=3,
        description="The number of results to return in a single response.",
    )
    current_page: Optional[int] = Field(
        default=0, description="Which page of the results to return."
    )
    generate_summaries: Optional[bool] = Field(
        default=False,
        description="Whether to generate any new summaries. In case the ruling already has a summary in DB, it will return that.",
    )


class RulingQuestionRequest(BaseModel):
    question: str = Field(
        description="Question to the LLM about a ruling.",
        example="Kolik bylo v případu žalobců?",
        max_length=250,
    )


class RulingQuestionResponse(BaseModel):
    answer: str = Field(description="The LLM's answer to a question (request).")


class SearchRulingsResponse(BaseModel):
    rulings: list[Ruling] = Field(
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
