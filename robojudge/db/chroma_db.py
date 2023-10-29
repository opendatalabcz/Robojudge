from typing import Optional
import uuid
import os
from typing import Dict
from itertools import zip_longest
import unittest.mock

from pydantic import BaseModel
import chromadb
import chromadb.config

from robojudge.components.chunker import split_text_into_embeddable_chunks
from robojudge.utils.settings import settings
from robojudge.utils.logger import logging
from robojudge.utils.internal_types import Case, CaseChunk

logger = logging.getLogger(__name__)


class CasesInChromaDB(BaseModel):
    embeddings: Optional[list[str]] = None
    documents: list[str] = []
    metadatas: list[Dict] | None = []
    ids: list[str] = []


class CaseEmbeddingStorage:
    COLLECTION_NAME = "cases"
    client: chromadb.PersistentClient

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.EMBEDDING_DB_HOST,
            port=settings.EMBEDDING_DB_PORT,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=CaseEmbeddingStorage.COLLECTION_NAME
        )
        logger.info(
            f'Connection to established to ChromaDB "{settings.EMBEDDING_DB_HOST}:{settings.EMBEDDING_DB_PORT}".'
        )

    # Enables to be used as a FastAPI dependency which needs a callable
    def __call__(self):
        return self

    @staticmethod
    def generate_id(name: str):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

    @staticmethod
    def cast_to_case_chunks(cases_from_db: CasesInChromaDB) -> list[CaseChunk]:
        """Parses a dict of lists into a list of pydantic models (`CaseChunk`)"""
        cases: list[CaseChunk] = []

        for id, metadata, document in zip_longest(
            cases_from_db.ids or [], cases_from_db.metadatas, cases_from_db.documents
        ):
            cases.append(
                CaseChunk(
                    chunk_id=id,
                    metadata=metadata,
                    chunk_text=document,
                    chunk_index=metadata["chunk_index"],
                    case_id=metadata["case_id"],
                )
            )

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
        if not len(cases):
            logging.warning("No cases provided to upsert into chromaDB")
            return

        cases_for_db = CasesInChromaDB()
        for case in cases:
            # Only the most important metadata are stored here
            # For more details, MongoDB is queried
            metadata = {
                "case_id": case.case_id,
                "jednaci_cislo": case.metadata.jednaci_cislo,
            }

            chunks = split_text_into_embeddable_chunks(case.reasoning)

            for chunk_index, chunk in enumerate(chunks):
                cases_for_db.documents.append(chunk)
                cases_for_db.metadatas.append({**metadata, "chunk_index": chunk_index})
                cases_for_db.ids.append(
                    CaseEmbeddingStorage.generate_id(f"{case.case_id}_{chunk_index}")
                )

        self.collection.upsert(**cases_for_db.dict())

    def get_all_cases(self):
        case_chunks_from_db = CasesInChromaDB(**self.collection.get(ids=[], where={}))
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def get_case_chunks_by_chunk_id(self, case_ids: list[str]):
        case_chunks_from_db = CasesInChromaDB(**self.collection.get(ids=case_ids))
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def get_case_chunks_by_case_id(self, case_ids: list[str]):
        query_result = CaseEmbeddingStorage.parse_text_query_result(
            self.collection.query(query_texts="", where={"case_id": {"$in": case_ids}})
        )
        return CaseEmbeddingStorage.cast_to_case_chunks(CasesInChromaDB(**query_result))

    def delete_case_chunks(self, case_ids: list[str]):
        return self.collection.delete(ids=case_ids)

    def find_case_chunks_by_text(
        self,
        query_text: str,
        limit: int = 5,
        included_fields: list[str] = ["documents", "metadatas"],
    ) -> list[CaseChunk]:
        query_result = CaseEmbeddingStorage.parse_text_query_result(
            self.collection.query(
                query_texts=[query_text], n_results=limit, include=included_fields
            )
        )
        return CaseEmbeddingStorage.cast_to_case_chunks(CasesInChromaDB(**query_result))


if os.environ.get("ENV") == "test":
    print("Detected testing environment -> creating test ChromaDB.")
    embedding_db = unittest.mock.Mock(spec=CaseEmbeddingStorage)
else:
    embedding_db = CaseEmbeddingStorage()


