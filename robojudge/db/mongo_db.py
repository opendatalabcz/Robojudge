from pymongo import MongoClient, ReplaceOne, UpdateOne

from robojudge.utils.settings import settings
from robojudge.utils.logger import logging
from robojudge.utils.internal_types import Case, CaseWithSummary

logger = logging.getLogger(__name__)


class DocumentStorage:
    client: MongoClient
    DB_NAME = "cases"
    COLLECTION_NAME = "metadata"

    def __init__(self) -> None:
        self.client = MongoClient(
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
    def collection(self):
        return self.client[self.DB_NAME][self.COLLECTION_NAME]

    def find_latest_case_id(self):
        try:
            cases = self.collection.find().sort("$natural", -1).limit(1)
            cases = list(cases)
            if len(cases) < 1:
                return settings.OLDEST_KNOWN_CASE_ID

            return int(list(cases)[0]["case_id"])
        except Exception:
            logging.exception(f"Error while searching for latest case_id:")

    def upsert_documents(self, cases: list[Case]):
        if len(cases) < 1:
            logging.warning("No documents to upsert to MongoDB")
            return

        try:
            updates = [
                ReplaceOne(
                    {"case_id": case.id},
                    {"case_id": case.id, **case.dict(exclude={"id"})},
                    upsert=True,
                )
                for case in cases
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logging.exception(f'Error while upserting metadata: "{cases}":')

    def add_document_summaries(self, summaries: list[CaseWithSummary]):
        if len(summaries) < 1:
            return

        try:
            logger.info('Saving generated summaries.')
            updates = [
                UpdateOne(
                    {"case_id": summary.id}, {"$set": {"summary": summary.summary}}
                )
                for summary in summaries
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logging.exception(f"Error while adding summaries {summaries}:")

    def delete_documents(self, case_ids: list[str]):
        try:
            self.collection.delete_many({"case_id": {"$in": case_ids}})
        except Exception:
            logging.exception(f"Error while deleting metadata with ids {case_ids}:")


document_db = DocumentStorage()
