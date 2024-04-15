from typing import Optional
import datetime

from pydantic import BaseModel, Field


class RulingMetadata(BaseModel):
    jednaci_cislo: str = Field(
        description="Identification string used in the Czech legal system. For the purposes of the API, 'spisová značka' is understood to be the same thing as 'číslo jednací'.",
        example="19 C 77/2023-44",
    )
    url: str = Field(
        description="URL of the ruling in JSON format",
        example="https://rozhodnuti.justice.cz/api/finaldoc/6d5da321-1c07-499b-8c27-f03b748d7792",
    )
    type: str = Field(
        default="",
        description="Type of ruling",
        example="JUDGEMENT",
    )
    court: str = Field(
        default="",
        description="Name of the court handing down the ruling.",
        example="Okresní soud ve Zlíně",
    )
    subject_matter: str = Field(
        description="A short description of the subject matter",
        example="rozvod manželství",
    )
    judge_name: str = Field(
        description="Full name of the judge handing down the ruling."
    )
    sentence_date: datetime.datetime = Field(
        description="Date of handing down the ruling."
    )
    publication_date: datetime.datetime = Field(
        description="Date of publishing the ruling on the justice.cz website."
    )
    ecli_id: str = Field(
        default="",
        description="European case law identifier",
        example="ECLI:CZ:OSZL:2023:19.C.77.2023.1",
    )
    keywords: list[str] = Field(
        default=[],
        description="List of words (usually legal terms) pertaining to the ruling.",
        example=["rozvod manželství", "výživné"],
    )
    regulations_mentioned: list[str] = Field(
        default=[],
        description="List of regulations related to the ruling.",
        example=["§ 23 z. č. 292/2013 Sb.", "§ 757 z. č. 89/2012 Sb"],
    )
    related_rulings: list[str] = Field(
        default=[], description="List of ruling 'jednací číslo' related to this ruling."
    )


class Ruling(BaseModel):
    ruling_id: str = Field(
        description="This ID corresponds to an uuid used by the Justice Ministry's website"
    )
    metadata: RulingMetadata
    verdict: str = Field(default="", description='"výrok" in Czech')
    reasoning: str = Field(default="", description='"odůvodnění" in Czech')
    summary: Optional[str] = Field(
        default="", description="A summary of the ruling's reasoning generated by an LLM"
    )
    title: Optional[str] = Field(
        default="",
        description="'Eye-catching' title generated by an LLM from the summary",
    )


class ChunkMetadata(BaseModel):
    chunk_index: int = Field(description="Used to sort chunks of the same ruling")
    jednaci_cislo: str
    ruling_id: str
    sentence_date: Optional[float] = None
    publication_date: Optional[float] = None
    court: Optional[str] = ""
    distance: Optional[float] = Field(
        description="Measure of how similar the chunk was to the query text."
    )


class RulingChunk(BaseModel):
    chunk_id: str = Field(description="Not ruling_id but the internal ChromaDB id")
    metadata: ChunkMetadata


class FetchJob(BaseModel):
    date: str
    started_at: datetime.datetime
    ruling_ids: list[str]