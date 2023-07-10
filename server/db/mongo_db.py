from pymongo import MongoClient, ReplaceOne
from bson.objectid import ObjectId

from utils.settings import settings
from utils.logger import logging
from utils.types import Metadata, Case

# TODO: index by case_id
# TODO: use motor

class CaseMetadataStorage:
    client: MongoClient

    def __init__(self) -> None:
        self.client = MongoClient(settings.MONGODB_URL)
        logging.info('Connection to MongoDB established.')

    @property
    def collection(self):
        return self.client['cases']['metadata']

    def find_latest_case_id(self):
        try:
            cases = self.collection.find().sort("$natural", -1).limit(1)
            if not cases:
                return 0

            return int(cases[0]["case_id"])
        except Exception:
            logging.exception(
                f'Error while searching for latest case_id:')

    # def find_metadata(self, query, projection=None):
    #     try:
    #         return self.collection.find(query, projection)
    #     except Exception:
    #         logging.exception(
    #             f'Error while querying metadata with "{query}" "{projection}":')

    def upsert_metadata(self, cases: list[Case]):
        try:
            updates = [
                ReplaceOne({"case_id": case.id},
                           {"case_id": case.id, **case.metadata.dict()},
                           upsert=True) for case in cases
            ]

            self.collection.bulk_write(updates)
        except Exception:
            logging.exception(
                f'Error while upserting metadata with case_ids "{[case.id for case in cases]}":')

    def delete_metadata(self, case_ids: list[str]):
        try:
            self.collection.delete_many({"case_id": {"$in": case_ids}})
        except Exception:
            logging.exception(
                f'Error while deleting metadata with ids {case_ids}:')


metadata_db = CaseMetadataStorage()
