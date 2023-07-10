from typing import List, Optional
import uuid

import more_itertools
import chromadb
import chromadb.config
from chromadb.utils import embedding_functions

from model.embedding import embedder
from utils.settings import settings
from utils.logger import logging
from utils.types import Case

PARAGRAPH_BATCH_SIZE = 4


class CaseEmbeddingStorage:
    def __init__(self):
        self.client = chromadb.Client(
            chromadb.config.Settings(
                chroma_api_impl="rest",
                chroma_server_host="localhost",
                chroma_server_http_port=8000
            ))
        logging.info('Connection to ChromaDB established.')

    @staticmethod
    def generate_id(name: str):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

    # TODO: just use a collection, do not specify it in all methods
    # TODO: Add custom embedder
    def create_collection(self, col_name: str):
        self.client.create_collection(
            col_name, get_or_create=True, embedding_function=embedding_functions.DefaultEmbeddingFunction())
        logging.info(f'Created collection "{col_name}".')

    def delete_collection(self, col_name: str):
        self.client.delete_collection(col_name)
        logging.info(f'Deleted collection "{col_name}".')

    def get_collection(self, col_name: str):
        return self.client.get_or_create_collection(col_name,  embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(settings.EMBEDDING_MODEL))

    def insert_documents(self, col_name: str, cases: List[Case]):
        collection = self.get_collection(col_name)

        parsed_documents = {
            # "embeddings": [],
            "documents": [],
            "metadatas": [],
            "ids": [],
        }

        for case in cases:
            metadata = {
                "case_id": case.id,
                "jednaci_cislo": case.metadata.jednaci_cislo,
                "verdict": case.verdict,
            }
            paragraphs = case.reasoning.split('\n')
            for batch_index, batch in enumerate(more_itertools.chunked(paragraphs, PARAGRAPH_BATCH_SIZE)):
                prepared_batch = '\n'.join(batch)
                # parsed_documents["embeddings"].append(list(embedder.embed_text(document.reasoning)))
                parsed_documents["documents"].append(prepared_batch)
                parsed_documents["metadatas"].append(
                    {**metadata, "batch_index": batch_index})
                parsed_documents["ids"].append(
                    CaseEmbeddingStorage.generate_id(case.id + str(batch_index)))

        collection.add(**parsed_documents)

    def get_documents(self, col_name: str, doc_ids: List[str]):
        collection = self.get_collection(col_name)

        return collection.get(ids=doc_ids)

    def delete_documents(self, col_name: str, doc_ids: List[str]):
        collection = self.get_collection(col_name)

        collection.delete(ids=doc_ids)

    def query_documents(self, col_name: str, query_text: str, include_n: Optional[int] = 5):
        collection = self.get_collection(col_name)

        return collection.query(query_texts=[query_text], n_results=include_n, include=[
            'documents', 'metadatas'])


embedding_db = CaseEmbeddingStorage()
