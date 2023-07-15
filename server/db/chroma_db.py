from typing import Optional
import uuid
from typing import Dict
from itertools import zip_longest

from pydantic import BaseModel
import more_itertools
import chromadb
import chromadb.config
from chromadb.utils import embedding_functions

from server.model.embedding import embedder
from server.utils.settings import settings
from server.utils.logger import logging
from server.utils.types import Case, CaseChunk

PARAGRAPH_BATCH_SIZE = 4


class CasesInChromaDB(BaseModel):
    # TODO: test different embeddings
    embeddings: list[str] | None = []
    documents: list[str] = []
    metadatas: list[Dict] | None = []
    ids: list[str] = []


class CaseEmbeddingStorage:
    client: chromadb.Client

    def __init__(self):
        self.client = chromadb.Client(
            chromadb.config.Settings(
                chroma_api_impl="rest",
                chroma_server_host=settings.EMBEDDING_DB_HOST,
                chroma_server_http_port=settings.EMBEDDING_DB_PORT,
                anonymized_telemetry=False,
            ))
        logging.info(
            f'Connection to established to ChromaDB "{settings.EMBEDDING_DB_HOST}:{settings.EMBEDDING_DB_PORT}".')

    @property
    def collection(self):
        COLLECTION_NAME = 'cases'
        return self.client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(settings.EMBEDDING_MODEL))

    @staticmethod
    def generate_id(name: str):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

    @staticmethod
    def cast_to_case_chunks(cases_from_db: CasesInChromaDB) -> list[CaseChunk]:
        """Parses a dict of lists into a list of pydantic models (`CaseChunk`)
        """
        cases: list[CaseChunk] = []

        for id, metadata, document in zip_longest(cases_from_db.ids or [], cases_from_db.metadatas, cases_from_db.documents):
            cases.append(CaseChunk(chunk_id=id, metadata=metadata,
                         chunk_text=document, chunk_index=metadata['chunk_index'], case_id=metadata['case_id']))

        return cases

    @staticmethod
    def parse_text_query_result(query_result):
        """
        The format is `(for whatever reason) { "documents": [ [ 'text1', 'text2', ... ] ], ... }`
        """
        parsed_result = {}
        for field, value in query_result.items():
            if value:
                parsed_result[field] = value[0] or []

        return parsed_result

    def upsert_cases(self, cases: list[Case]):
        cases_for_db = CasesInChromaDB()
        for case in cases:
            # Only the most important metadata are stored here
            # For more details, MongoDB is queried
            metadata = {
                "case_id": case.id,
                "jednaci_cislo": case.metadata.jednaci_cislo,
                # TODO: consider omitting
                "verdict": case.verdict,
            }

            # Create chunks of the case's reasoning and create embeddings of these chunks
            paragraphs = case.reasoning.split('\n')
            paragraph_chunks = more_itertools.chunked(
                paragraphs, PARAGRAPH_BATCH_SIZE)
            paragraph_chunks = ['\n'.join(chunk) for chunk in paragraph_chunks]

            cases_for_db.embeddings.extend(
                embedder.embed_texts(paragraph_chunks))

            for chunk_index, chunk in enumerate(paragraph_chunks):
                cases_for_db.documents.append(chunk)
                cases_for_db.metadatas.append(
                    {**metadata, "chunk_index": chunk_index})
                cases_for_db.ids.append(
                    CaseEmbeddingStorage.generate_id(f'{case.id}_{chunk_index}'))

        self.collection.upsert(**cases_for_db.dict())

    def get_all_cases(self):
        case_chunks_from_db = CasesInChromaDB(**self.collection.get(ids=[]))
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def get_case_chunks_by_id(self, case_ids: list[str]):
        case_chunks_from_db = CasesInChromaDB(
            **self.collection.get(ids=case_ids))
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def delete_case_chunks(self, case_ids: list[str]):
        return self.collection.delete(ids=case_ids)

    def find_case_chunks_by_text(self, query_text: str, limit: int = 5, included_fields: list[str] = ['documents', 'metadatas']) -> list[CaseChunk]:
        query_result = CaseEmbeddingStorage.parse_text_query_result(self.collection.query(
            query_texts=[query_text], n_results=limit, include=included_fields))
        return CaseEmbeddingStorage.cast_to_case_chunks(CasesInChromaDB(**query_result))


embedding_db = CaseEmbeddingStorage()
