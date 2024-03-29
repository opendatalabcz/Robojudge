import asyncio
import multiprocessing.pool


from robojudge.db.mongo_db import document_db
from robojudge.db.chroma_db import embedding_db
from robojudge.utils.logger import logging

logger = logging.getLogger(__name__)

async def run_migration():
    pool = multiprocessing.pool.ThreadPool(processes=1)

    rulings = document_db.collection.find()
    pool.map(migrate_ruling, rulings)

    logger.info('Migration is finished.')

    pool.close()


def migrate_ruling(ruling: dict):
    ruling_chunks = embedding_db.parse_text_query_result(embedding_db.collection.query(query_texts="", where={
        "case_id": {"$in": [ruling['case_id']]}}))

    for metadata in ruling_chunks['metadatas']:
        metadata['sentence_date'] = ruling['metadata']['sentence_date'].timestamp()
        metadata['publication_date'] = ruling['metadata']['publication_date'].timestamp()
        metadata['court'] = ruling['metadata']['court']
    try:
        embedding_db.collection.update(
            ids=ruling_chunks['ids'], metadatas=ruling_chunks['metadatas'])
    except Exception as e:
        logger.info(
            f'Error while updating chunks {ruling_chunks.get("ids", [])}: {e}')

    logger.info(f'Updated chunks for ruling with id {ruling["case_id"]}.')


if __name__ == '__main__':
    asyncio.run(run_migration())
