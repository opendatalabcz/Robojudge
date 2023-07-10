import asyncio
from multiprocessing import Queue, Process

import more_itertools
from concurrent.futures import ThreadPoolExecutor

from server.db.chroma_db import embedding_db
from server.db.mongo_db import metadata_db
from server.scraper.case_page_scraper import CasePageScraper
from server.db.mongo_db import metadata_db
from server.utils.logger import logging

BATCH_SIZE = 10
TOTAL_SCRAPE_SIZE=100
SCRAPER_THREAD_COUNT = 3
PARSER_THREAD_COUNT = 3

async def fetch_new_cases():
    # latest_id = await CasePageScraper.get_newest_case_id()
    latest_id_in_db = metadata_db.find_latest_case_id() or 0

    case_ids_in_db = list(metadata_db.collection.find({}, {"case_id"}))
    case_ids_in_db = set(int(case['case_id']) for case in case_ids_in_db)

    case_ids = set(range(latest_id_in_db + 1, latest_id_in_db + TOTAL_SCRAPE_SIZE + 1)).difference(case_ids_in_db)

    q = Queue()

    parsers = []
    for _ in range(PARSER_THREAD_COUNT):
        parser = Process(target=parser_worker, args=(q,))
        parser.start()
        parsers.append(parser)

    case_id_chunks = more_itertools.chunked(case_ids, BATCH_SIZE)
    with ThreadPoolExecutor(max_workers=SCRAPER_THREAD_COUNT, thread_name_prefix='scraper') as executor:
        coroutines = [(scrape_cases(chunk), index)
                      for index, chunk in enumerate(case_id_chunks)]
        for index, result in enumerate(executor.map(scraper_worker, coroutines)):
            logging.info(f'Finished case batch #{index}')
            q.put(result)

    q.put('DONE')

    for parser in parsers:
        parser.join()


# Has to be wrapped because of its async nature
def scraper_worker(params):
    coroutine, id = params
    return asyncio.run(coroutine)


async def scrape_cases(case_ids):
    return await asyncio.gather(*[CasePageScraper(case_id).scrape_case() for case_id in case_ids])


def parser_worker(q):
    while True:
        cases = q.get()
        if cases == 'DONE':
            q.put('DONE')
            break
        try:
            filtered_cases = [case for case in cases if case]
            embedding_db.insert_documents('testzz', filtered_cases)
            metadata_db.upsert_metadata(filtered_cases)
        except Exception:
            logging.exception(f'Error while reading cases:')


async def writer_worker(params):
    case_ids, q = params
    cases = await asyncio.gather(*[CasePageScraper(case_id).scrape_case() for case_id in case_ids])
    await q.put(cases)
