import os
import datetime

import pymongo
from pymongo import ReplaceOne, UpdateOne
from pymongo.collection import Collection
import mongomock

from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.utils.internal_types import Case


class DocumentStorage:
    client: pymongo.MongoClient
    DB_NAME = "robojudge_case_db"
    COLLECTION_NAME = "cases"
    SCRAPING_INFORMATION_COLLECTION_NAME = "scraping"
    SCRAPING_JOB_COLLECTION_NAME = "fetch_jobs"

    def __init__(self) -> None:
        self.client = pymongo.MongoClient(
            host=settings.DOCUMENT_DB_HOST, port=settings.DOCUMENT_DB_PORT
        )
        logger.info(
            f'Connection established to MongoDB "{settings.DOCUMENT_DB_HOST}:{settings.DOCUMENT_DB_PORT}".'
        )

        self.collection.create_index("case_id")

    # Enables to be used as a FastAPI dependency which needs a callable
    def __call__(self):
        return self

    # Searching is done through the collection object directly
    @property
    def collection(self) -> Collection[Case]:
        return self.client[self.DB_NAME][self.COLLECTION_NAME]

    @property
    def scraping_job_collection(self):
        return self.client[self.DB_NAME][self.SCRAPING_JOB_COLLECTION_NAME]

    def find_latest_case_id(self):
        try:
            cases = (
                self.scraping_job_collection.find().sort("last_ruling_id", -1).limit(1)
            )
            cases = list(cases)
            if len(cases) > 0:
                last_case_id = int(list(cases)[0]["last_ruling_id"])
                return (
                    last_case_id
                    if last_case_id > settings.OLDEST_KNOWN_CASE_ID
                    else settings.OLDEST_KNOWN_CASE_ID
                )

            # Try to deduce last case from cases themselves if scraping metadata are missing
            cases = self.collection.find().sort("$natural", -1).limit(1)
            cases = list(cases)
            if len(cases) > 0:
                return int(list(cases)[0]["case_id"])

            return settings.OLDEST_KNOWN_CASE_ID

        except Exception:
            logger.exception("Error while searching for latest case_id:")

    def upsert_documents(self, cases: list[Case]):
        if len(cases) < 1:
            logger.warning("No documents to upsert to MongoDB")
            return

        try:
            updates = [
                ReplaceOne(
                    {"case_id": case.case_id},
                    {**case.dict(), "created_at": datetime.datetime.now()},
                    upsert=True,
                )
                for case in cases
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logger.exception(f'Error while upserting metadata: "{cases}":')

    def add_document_summaries(self, summaried_cases: list[Case]):
        if len(summaried_cases) < 1:
            return

        try:
            logger.info("Saving generated summaries.")
            updates = [
                UpdateOne(
                    {"case_id": summaried_case.case_id},
                    {"$set": {"summary": summaried_case.summary}},
                )
                for summaried_case in summaried_cases
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logger.exception(f"Error while adding summaries {summaried_cases}:")

    def delete_documents(self, case_ids: list[str]):
        try:
            self.collection.delete_many({"case_id": {"$in": case_ids}})
        except Exception:
            logger.exception(f"Error while deleting metadata with ids {case_ids}:")


@mongomock.patch(servers=((settings.DOCUMENT_DB_HOST, settings.DOCUMENT_DB_PORT),))
def create_test_db():
    return DocumentStorage()


if os.environ.get("ENV") == "test":
    print("Detected testing environment -> creating test MongoDB.")
    document_db = create_test_db()
else:
    document_db = DocumentStorage()
