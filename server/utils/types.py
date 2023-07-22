from strenum import StrEnum
from pydantic import BaseModel, Field


class CaseMetadataAttributes(StrEnum):
    JEDNACI_CISLO = 'jednaci_cislo'
    COURT = 'court'
    JUDGE_NAME = 'judge_name'
    ECLI_ID = 'ecli_id'
    SUBJECT_MATTER = 'subject_matter'
    SENTENCE_DATE = 'sentence_date'
    PUBLICATION_DATE = 'publication_date'
    KEYWORDS = 'keywords'
    REGULATIONS_MENTIONED = 'regulations_mentioned'
    RELATED_CASES = 'related_cases'


DOCUMENT_METADATA_MAP = {
    "Jednací číslo": CaseMetadataAttributes.JEDNACI_CISLO,
    "Soud": CaseMetadataAttributes.COURT,
    "Autor": CaseMetadataAttributes.JUDGE_NAME,
    "Identifikátor ECLI": CaseMetadataAttributes.ECLI_ID,
    "Předmět řízení": CaseMetadataAttributes.SUBJECT_MATTER,
    "Datum vydání": CaseMetadataAttributes.SENTENCE_DATE,
    "Datum zveřejnění": CaseMetadataAttributes.PUBLICATION_DATE,
    "Klíčová slova": CaseMetadataAttributes.KEYWORDS,
    "Zmíněná ustanovení": CaseMetadataAttributes.REGULATIONS_MENTIONED,
    "Vztah k jiným rozhodnutím": CaseMetadataAttributes.RELATED_CASES,
}


class Metadata(BaseModel):
    jednaci_cislo: str
    court: str
    subject_matter: str
    judge_name: str
    sentence_date: str
    publication_date: str
    ecli_id: str = ''
    keywords: list[str] = []
    regulations_mentioned: list[str] = []
    related_cases: list[str] = []


class Case(BaseModel):
    id: str
    metadata: Metadata
    verdict: str = ''
    reasoning: str = ''

class CaseChunk(BaseModel):
    chunk_id: str = Field(description='Not case_id but the internal ChromaDB id')
    chunk_index: int
    case_id: str
    chunk_text: str
    metadata: dict

class CaseWithSummary(Case):
    summary: str = ''