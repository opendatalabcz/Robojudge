from typing import Any
import uuid
import os
from itertools import zip_longest
import unittest.mock

import chromadb
import chromadb.config
from chromadb.utils import embedding_functions

from robojudge.components.chunker import TextChunker
from robojudge.utils.api_types import CaseSearchRequestFilters
from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.utils.internal_types import (
    Case,
    CaseChunk,
    ChunkMetadata,
)


class CaseEmbeddingStorage:
    COLLECTION_NAME = "cases"
    client: chromadb.PersistentClient
    embedding_function: embedding_functions.DefaultEmbeddingFunction

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.EMBEDDING_DB_HOST,
            port=settings.EMBEDDING_DB_PORT,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=CaseEmbeddingStorage.COLLECTION_NAME,
        )

        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        logger.info(
            f'Connection to established to ChromaDB "{settings.EMBEDDING_DB_HOST}:{settings.EMBEDDING_DB_PORT}".'
        )

    # Enables to be used as a FastAPI dependency which needs a callable
    def __call__(self):
        return self

    def upsert_cases(self, cases: list[Case]):
        """
        Upserts chunks of the provided texts alongside selected metadata.
        IDs are generated in a deterministic way, so duplicates do not occur.
        """
        if not len(cases):
            logger.warning("No cases provided to upsert into chromaDB")
            return

        cases_for_db = {"documents": [], "metadatas": [], "ids": [], "embeddings": []}
        for case in cases:
            # Only the most important metadata are stored here
            # For more details, MongoDB is queried
            metadata = {
                "case_id": case.case_id,
                "jednaci_cislo": case.metadata.jednaci_cislo,
                "sentence_date": case.metadata.sentence_date.timestamp(),
                "publication_date": case.metadata.publication_date.timestamp(),
                "court": case.metadata.court,
            }

            chunks = TextChunker.split_text_into_embeddable_chunks(case.reasoning)

            # Don't put the actual text into the DB, only generate the embedding
            cases_for_db["embeddings"].extend(self.collection._embed(input=chunks))
            for chunk_index in range(len(chunks)):
                cases_for_db["documents"].append("")
                cases_for_db["metadatas"].append(
                    {**metadata, "chunk_index": chunk_index}
                )
                cases_for_db["ids"].append(
                    CaseEmbeddingStorage.generate_id(f"{case.case_id}_{chunk_index}")
                )

        self.collection.upsert(**cases_for_db)

    def get_all_case_chunks(self) -> list[CaseChunk]:
        """
        Returns all chunks in the database.
        """
        case_chunks_from_db = self.collection.get(ids=[], where={})
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def get_case_chunks_by_chunk_id(self, chunk_ids: list[str]) -> list[CaseChunk]:
        case_chunks_from_db = self.collection.get(ids=chunk_ids)
        return CaseEmbeddingStorage.cast_to_case_chunks(case_chunks_from_db)

    def get_case_chunks_by_case_id(self, case_ids: list[str]) -> list[CaseChunk]:
        query_result = self.collection.query(
            query_texts="", where={"case_id": {"$in": case_ids}}
        )
        return CaseEmbeddingStorage.parse_text_query_result(query_result)

    def delete_case_chunks(self, case_ids: list[str]):
        return self.collection.delete(ids=case_ids)

    def find_rulings_by_text(
        self, query_text: str, offset: int = 0, n_results: int = 5, filters: dict = None
    ) -> list[CaseChunk]:
        """
        Returns rulings corresponding to the query text (at most once even if multiple chunks are found for that ruling).
        Supports pagination with `offset` and `n_results`.
        If `query_text` is too long, it will be split into chunks used in the DB itself.
        """
        chunks = self.find_case_chunks_by_text(query_text, filters)
        unique_ruling_ids = set()
        unique_chunks = []
        for chunk in chunks:
            if chunk.metadata.case_id not in unique_ruling_ids:
                unique_ruling_ids.add(chunk.metadata.case_id)
                unique_chunks.append(chunk)

        return sorted(unique_chunks, key=lambda x: x.metadata.distance)[
            offset : offset + n_results
        ]

    def find_case_chunks_by_text(
        self,
        query_text: str,
        filters: dict = None,
    ) -> list[CaseChunk]:
        """
        Returns chunks corresponding to the query text.
        Supports pagination with `offset` and `n_results`.
        Suports filtering and projection (`included_fields`).
        If `query_text` is too long, it will be split into chunks used in the DB itself.
        """
        where_clauses = CaseEmbeddingStorage.parse_filters(filters)
        query_texts = TextChunker.split_text_into_embeddable_chunks(query_text)

        query_result = self.collection.query(
            query_texts=query_texts,
            n_results=settings.MAX_SEARCHABLE_RULING_COUNT,
            where=where_clauses,
        )

        parsed_chunks = CaseEmbeddingStorage.parse_text_query_result(query_result)
        return parsed_chunks

    @staticmethod
    def generate_id(name: str):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

    @staticmethod
    def cast_to_case_chunks(cases_from_db: list[list]) -> list[CaseChunk]:
        """Parses a dict of lists into a list of pydantic models (`CaseChunk`)"""
        cases: list[CaseChunk] = []

        for id, metadata in zip_longest(
            cases_from_db["ids"] or [],
            cases_from_db["metadatas"],
        ):
            cases.append(
                CaseChunk(
                    chunk_id=id,
                    metadata=metadata,
                )
            )

        return cases

    @staticmethod
    def parse_text_query_result(query_result: dict[list[list]]) -> list[CaseChunk]:
        """
        Flattens and parses a list of lists for properties like ids, texts, etc.
        """
        results = []
        for ids, metadatas, distances in zip(
            query_result["ids"],
            query_result["metadatas"],
            query_result["distances"],
        ):
            for (
                id,
                metadata,
                distance,
            ) in zip(ids, metadatas, distances):
                chunk_metadata = ChunkMetadata(**metadata, distance=distance)
                results.append(CaseChunk(chunk_id=id, metadata=chunk_metadata))

        return results

    @staticmethod
    def parse_filters(filters: CaseSearchRequestFilters):
        """
        Translates a dictionary of potential filters into Chroma query language.
        """
        where_clauses = {"$and": []}

        def construct_where_clause(field: str, operator: str, value: Any):
            return {field: {operator: value}}

        for filter_key, filter_value in filters.dict().items():
            if not filter_value:
                continue

            match filter_key:
                case "publication_date_from":
                    where_clauses["$and"].append(
                        construct_where_clause("publication_date", "$gte", filter_value)
                    )
                case "publication_date_to":
                    where_clauses["$and"].append(
                        construct_where_clause("publication_date", "$lte", filter_value)
                    )
                case "sentence_date_from":
                    where_clauses["$and"].append(
                        construct_where_clause("sentence_date", "$gte", filter_value)
                    )
                case "sentence_date_to":
                    where_clauses["$and"].append(
                        construct_where_clause("sentence_date", "$lte", filter_value)
                    )

        if not len(where_clauses["$and"]):
            return {}

        if len(where_clauses["$and"]) == 1:
            where_clauses = where_clauses["$and"][0]

        return where_clauses


if os.environ.get("ENV") == "test":
    print("Detected testing environment -> creating test ChromaDB.")
    embedding_db = unittest.mock.Mock(spec=CaseEmbeddingStorage)
else:
    embedding_db = CaseEmbeddingStorage()
