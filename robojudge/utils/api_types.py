from typing import Optional

from pydantic import BaseModel, Field


class CaseSearchRequest(BaseModel):
    query_text: str = Field(
        description="Any string of text which should have similar cases in the DB. Longer texts have more accurate results."
    )
    max_results: Optional[int] = Field(
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
