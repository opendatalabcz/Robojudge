from typing import List
import uuid

import chromadb
import chromadb.config

from utils.logger import logging
from utils.types import Document, Optional

# TODO: Actual DB server
logger = logging.getLogger(__name__)


class DB:
    def __init__(self):
        self.client = chromadb.Client(
            chromadb.config.Settings()
        )

    @staticmethod
    def generate_id(name: str):
        return uuid.uuid5(uuid.NAMESPACE_URL, name)

    def create_collection(self, col_name: str):
        if self.client.get_collection(col_name):
            logger.warn(f'Collection "{col_name}" already exists.')
            return

        self.client.create_collection(col_name)
        logger.info(f'Created collection "{col_name}".')

    def delete_collection(self, col_name: str):
        self.client.delete_collection(col_name)
        logger.info(f'Deleted collection "{col_name}".')

    def get_collection(self, col_name: str):
        return self.client.get_or_create_collection(col_name)

    # TODO: Split into smaller chunks
    def upsert_documents(self, col_name: str, documents: List[Document]):
        collection = self.get_collection(col_name)

        parsed_documents = {
            "documents": [],
            "metadatas": [],
            "ids": [],
        }

        for document in documents:
            parsed_documents["documents"].append(document.text)
            parsed_documents["metadatas"].append(
                {**document.metadata, "name": document.name})
            parsed_documents["ids"].append(DB.generate_id(document.name))

        collection.upsert(**parsed_documents)

    def get_documents(self, col_name: str, doc_ids: List[str]):
        collection = self.get_collection(col_name)

        collection.get(ids=doc_ids)

    def delete_documents(self, col_name: str, doc_ids: List[str]):
        collection = self.get_collection(col_name)

        collection.delete(ids=doc_ids)

    def query_documents(self, col_name: str, query_text: str, include_n: Optional[int] = 5):
        collection = self.get_collection(col_name)

        collection.query(query_texts=[query_text], n_results=include_n, include=[
                         'documents', 'metadatas'])
