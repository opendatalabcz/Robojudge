import datetime
from typing import Any
import uuid
import os
from itertools import zip_longest
import unittest.mock

import chromadb
import chromadb.config
from chromadb.utils import embedding_functions

from robojudge.components.chunker import TextChunker
from robojudge.utils.api_types import RulingSearchRequestFilters
from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.utils.internal_types import (
    Ruling,
    RulingChunk,
    ChunkMetadata,
)


class RulingEmbeddingStorage:
    COLLECTION_NAME = "rulings"
    client: chromadb.PersistentClient
    embedding_function: embedding_functions.DefaultEmbeddingFunction

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.EMBEDDING_DB_HOST,
            port=settings.EMBEDDING_DB_PORT,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=RulingEmbeddingStorage.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # l2 is the default
        )

        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        logger.info(
            f'Connection to established to ChromaDB "{settings.EMBEDDING_DB_HOST}:{settings.EMBEDDING_DB_PORT}".'
        )

    # Enables to be used as a FastAPI dependency which needs a callable
    def __call__(self):
        return self

    def upsert_rulings(self, rulings: list[Ruling]):
        """
        Upserts chunks of the provided texts alongside selected metadata.
        IDs are generated in a deterministic way, so duplicates do not occur.
        """
        if not len(rulings):
            logger.warning("No rulings provided to upsert into chromaDB")
            return

        try:
            rulings_for_db = {
                "documents": [],
                "metadatas": [],
                "ids": [],
                "embeddings": [],
            }
            for ruling in rulings:
                # Only the most important metadata are stored here
                # For more details, MongoDB is queried
                metadata = {
                    "ruling_id": ruling.ruling_id,
                    "jednaci_cislo": ruling.metadata.jednaci_cislo,
                    "sentence_date": ruling.metadata.sentence_date.timestamp(),
                    "publication_date": ruling.metadata.publication_date.timestamp(),
                    "court": ruling.metadata.court,
                }

                chunks = TextChunker.split_text_into_embeddable_chunks(ruling.reasoning)

                # Don't put the actual text into the DB, only generate the embedding
                rulings_for_db["embeddings"].extend(
                    self.collection._embed(input=chunks)
                )
                for chunk_index in range(len(chunks)):
                    rulings_for_db["documents"].append("")
                    rulings_for_db["metadatas"].append(
                        {**metadata, "chunk_index": chunk_index}
                    )
                    rulings_for_db["ids"].append(
                        RulingEmbeddingStorage.generate_id(
                            f"{ruling.ruling_id}_{chunk_index}"
                        )
                    )

            self.collection.upsert(**rulings_for_db)
        except Exception as e:
            logger.exception(f"Error while upserting rulings into ChromaDB: {e}")

    def get_all_ruling_chunks(self) -> list[RulingChunk]:
        """
        Returns all chunks in the database.
        """
        ruling_chunks_from_db = self.collection.get(ids=[], where={})
        return RulingEmbeddingStorage.cast_to_ruling_chunks(ruling_chunks_from_db)

    def get_ruling_chunks_by_chunk_id(self, chunk_ids: list[str]) -> list[RulingChunk]:
        ruling_chunks_from_db = self.collection.get(ids=chunk_ids)
        return RulingEmbeddingStorage.cast_to_ruling_chunks(ruling_chunks_from_db)

    def get_ruling_chunks_by_ruling_id(
        self, ruling_ids: list[str]
    ) -> list[RulingChunk]:
        query_result = self.collection.query(
            query_texts="", where={"ruling_id": {"$in": ruling_ids}}
        )
        return RulingEmbeddingStorage.parse_text_query_result(query_result)

    def delete_ruling_chunks(self, ruling_ids: list[str]):
        try:
            return self.collection.delete(ids=ruling_ids)
        except Exception as e:
            logger.exception(f"Error while deleting rulings from ChromaDB: {e}")

    def find_rulings_by_text(
        self, query_text: str, offset: int = 0, n_results: int = 5, filters: dict = None
    ) -> list[RulingChunk]:
        """
        Returns rulings corresponding to the query text (at most once even if multiple chunks are found for that ruling).
        Supports pagination with `offset` and `n_results`.
        If `query_text` is too long, it will be split into chunks used in the DB itself.
        """
        chunks = self.find_ruling_chunks_by_text(query_text, filters)
        unique_ruling_ids = set()
        unique_chunks = []
        for chunk in chunks:
            if chunk.metadata.ruling_id not in unique_ruling_ids:
                unique_ruling_ids.add(chunk.metadata.ruling_id)
                unique_chunks.append(chunk)

        return sorted(unique_chunks, key=lambda x: x.metadata.distance)[
            offset : offset + n_results
        ]

    def find_ruling_chunks_by_text(
        self,
        query_text: str,
        filters: dict = None,
    ) -> list[RulingChunk]:
        """
        Returns chunks corresponding to the query text.
        Supports pagination with `offset` and `n_results`.
        Suports filtering and projection (`included_fields`).
        If `query_text` is too long, it will be split into chunks used in the DB itself.
        """
        where_clauses = RulingEmbeddingStorage.parse_filters(filters)
        query_texts = TextChunker.split_text_into_embeddable_chunks(query_text)

        query_result = self.collection.query(
            query_texts=query_texts,
            n_results=settings.MAX_SEARCHABLE_RULING_COUNT,
            where=where_clauses,
        )

        parsed_chunks = RulingEmbeddingStorage.parse_text_query_result(query_result)
        return parsed_chunks

    @staticmethod
    def generate_id(name: str):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

    @staticmethod
    def cast_to_ruling_chunks(rulings_from_db: list[list]) -> list[RulingChunk]:
        """Parses a dict of lists into a list of pydantic models (`rulingChunk`)"""
        rulings: list[RulingChunk] = []

        for id, metadata in zip_longest(
            rulings_from_db["ids"] or [],
            rulings_from_db["metadatas"],
        ):
            rulings.append(
                RulingChunk(
                    chunk_id=id,
                    metadata=metadata,
                )
            )

        return rulings

    @staticmethod
    def parse_text_query_result(query_result: dict[list[list]]) -> list[RulingChunk]:
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
                print(metadata)
                chunk_metadata = ChunkMetadata(**metadata, distance=distance)
                results.append(RulingChunk(chunk_id=id, metadata=chunk_metadata))

        return results

    @staticmethod
    def parse_filters(filters: RulingSearchRequestFilters):
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
                        construct_where_clause(
                            "publication_date",
                            "$gte",
                            datetime.datetime.strptime(
                                filter_value, "%Y-%m-%d"
                            ).timestamp(),
                        )
                    )
                case "publication_date_to":
                    where_clauses["$and"].append(
                        construct_where_clause(
                            "publication_date",
                            "$lte",
                            datetime.datetime.strptime(
                                filter_value, "%Y-%m-%d"
                            ).timestamp(),
                        )
                    )
                case "sentence_date_from":
                    where_clauses["$and"].append(
                        construct_where_clause(
                            "sentence_date",
                            "$gte",
                            datetime.datetime.strptime(
                                filter_value, "%Y-%m-%d"
                            ).timestamp(),
                        )
                    )
                case "sentence_date_to":
                    where_clauses["$and"].append(
                        construct_where_clause(
                            "sentence_date",
                            "$lte",
                            datetime.datetime.strptime(
                                filter_value, "%Y-%m-%d"
                            ).timestamp(),
                        )
                    )

        if not len(where_clauses["$and"]):
            return {}

        if len(where_clauses["$and"]) == 1:
            where_clauses = where_clauses["$and"][0]

        return where_clauses


if os.environ.get("ENV") == "test":
    print("Detected testing environment -> creating test ChromaDB.")
    embedding_db = unittest.mock.Mock(spec=RulingEmbeddingStorage)
else:
    embedding_db = RulingEmbeddingStorage()
