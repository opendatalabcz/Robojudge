import os
import datetime

import pymongo
from pymongo import ReplaceOne, UpdateOne
from pymongo.collection import Collection
import mongomock

from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.utils.internal_types import Ruling


class DocumentStorage:
    client: pymongo.MongoClient
    DB_NAME = "robojudge_db"
    COLLECTION_NAME = "rulings"
    FETCH_JOB_COLLECTION_NAME = "fetch_jobs"

    def __init__(self) -> None:
        self.client = pymongo.MongoClient(
            host=settings.DOCUMENT_DB_HOST, port=settings.DOCUMENT_DB_PORT
        )
        logger.info(
            f'Connection established to MongoDB "{settings.DOCUMENT_DB_HOST}:{settings.DOCUMENT_DB_PORT}".'
        )

        self.collection.create_index("ruling_id")

    # Enables to be used as a FastAPI dependency which needs a callable
    def __call__(self):
        return self

    # Searching is done through the collection object directly
    @property
    def collection(self) -> Collection[dict]:
        return self.client[self.DB_NAME][self.COLLECTION_NAME]

    @property
    def fetch_job_collection(self) -> Collection[dict]:
        return self.client[self.DB_NAME][self.FETCH_JOB_COLLECTION_NAME]

    def upsert_rulings(self, rulings: list[Ruling]):
        if len(rulings) < 1:
            logger.warning("No rulings to upsert to MongoDB")
            return

        try:
            updates = [
                ReplaceOne(
                    {"ruling_id": ruling.ruling_id},
                    {**ruling.dict(), "created_at": datetime.datetime.now()},
                    upsert=True,
                )
                for ruling in rulings
            ]

            self.collection.bulk_write(updates)
        except Exception as e:
            logger.exception(f"Error while upserting rulings into MongoDB: {e}")

    def add_ruling_summaries_and_titles(self, summaried_rulings: list[Ruling]):
        if len(summaried_rulings) < 1:
            return

        try:
            logger.info("Saving generated summaries and titles.")
            updates = [
                UpdateOne(
                    {"ruling_id": summaried_ruling.ruling_id},
                    {
                        "$set": {
                            "summary": summaried_ruling.summary,
                            "title": summaried_ruling.title,
                        }
                    },
                )
                for summaried_ruling in summaried_rulings
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logger.exception(f"Error while adding summaries and titles {summaried_rulings}:")

    def delete_rulings(self, ruling_ids: list[str]):
        try:
            self.collection.delete_many({"ruling_id": {"$in": ruling_ids}})
        except Exception:
            logger.exception(
                f"Error while deleting rulings from MongoDB with ids {ruling_ids}:"
            )


@mongomock.patch(servers=((settings.DOCUMENT_DB_HOST, settings.DOCUMENT_DB_PORT),))
def create_test_db():
    return DocumentStorage()


if os.environ.get("ENV") == "test":
    print("Detected testing environment -> creating test MongoDB.")
    document_db = create_test_db()
else:
    document_db = DocumentStorage()
