import asyncio
import multiprocessing.pool
from pathlib import Path

from robojudge.db.mongo_db import document_db
from robojudge.db.chroma_db import embedding_db
from robojudge.utils.logger import logger

MEMORY_PATH = Path("/var/migration_successful")


async def run_migration():
    """
    One time migration that adds date metadata to Chroma entries.
    """
    if MEMORY_PATH.exists():
        logger.info(
            f"Migration skipped because it was already performed. Delete {MEMORY_PATH} file if you want to repeat it."
        )
        return

    pool = multiprocessing.pool.ThreadPool(processes=1)

    rulings = document_db.collection.find()
    pool.map(migrate_ruling, rulings)

    with open(MEMORY_PATH, "w") as wf:
        wf.write("done")

    logger.info("Migration is finished.")

    pool.close()


def migrate_ruling(ruling: dict):
    # ruling_chunks = embedding_db.get_case_chunks_by_case_id(case_ids=[ruling["case_id"]])
    try:
        ruling_chunks = embedding_db.collection.query(
            query_texts="", where={"case_id": {"$in": [ruling["case_id"]]}}
        )

        for metadata in ruling_chunks["metadatas"][0]:
            metadata["sentence_date"] = ruling["metadata"]["sentence_date"].timestamp()
            metadata["publication_date"] = ruling["metadata"][
                "publication_date"
            ].timestamp()
            metadata["court"] = ruling["metadata"]["court"]

            embedding_db.collection.update(
                ids=ruling_chunks["ids"][0], metadatas=ruling_chunks["metadatas"][0]
            )
    except Exception as e:
        logger.info(f'Error while updating chunks: {e}')

    logger.info(f'Updated chunks for ruling with id {ruling["case_id"]}.')


if __name__ == "__main__":
    asyncio.run(run_migration())
