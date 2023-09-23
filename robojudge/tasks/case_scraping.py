import asyncio
from multiprocessing import Queue, Process
from concurrent.futures import ThreadPoolExecutor

import more_itertools

from robojudge.utils.settings import settings
from robojudge.db.chroma_db import embedding_db
from robojudge.db.mongo_db import document_db
from robojudge.components.scraper.case_page_scraper import CasePageScraper
from robojudge.db.mongo_db import document_db
from robojudge.utils.logger import logging
from robojudge.utils.functional import periodic

FETCH_INTERVAL_IN_SECONDS=180
BATCH_SIZE = 10
MAX_SCRAPE_SIZE = 20
SCRAPER_THREAD_COUNT = 3
PARSER_PROCESS_COUNT = 3


async def determine_case_ids_to_parse():
    latest_id = await CasePageScraper.get_newest_case_id()
    latest_id_in_db = document_db.find_latest_case_id() or settings.OLDEST_KNOWN_CASE_ID

    case_ids_in_db = list(document_db.collection.find({}, {"case_id"}))
    case_ids_in_db = set(int(case['case_id']) for case in case_ids_in_db)

    lower = latest_id_in_db + 1
    upper = min(latest_id_in_db + MAX_SCRAPE_SIZE, latest_id) + 1

    return set(range(lower, upper)).difference(case_ids_in_db)


async def fetch_new_cases():
    case_ids = await determine_case_ids_to_parse()

    q = Queue()

    # Parsers are computation-intensive so separate processes are required
    parsers = []
    for index in range(PARSER_PROCESS_COUNT):
        parser = Process(target=parser_worker, args=(q,index))
        parser.start()
        parsers.append(parser)

    # Scraping is IO bound (waiting for the network to return), so asyncio with threads is enough
    case_id_chunks = more_itertools.chunked(case_ids, BATCH_SIZE)
    with ThreadPoolExecutor(max_workers=SCRAPER_THREAD_COUNT, thread_name_prefix='scraper') as executor:
        coroutines = [(scrape_cases(chunk), index)
                      for index, chunk in enumerate(case_id_chunks)]
        for index, result in enumerate(executor.map(scraper_worker, coroutines)):
            logging.info(f'Finished scraping case batch #{index}')
            q.put(result)

    q.put('DONE')

    for parser in parsers:
        parser.join()

    logging.info('All provided case_ids fetched.')


# Has to be wrapped because of its async nature
def scraper_worker(params):
    coroutine, batch_id = params
    logging.info(f'Initializing case batch #{batch_id}')
    return asyncio.run(coroutine)


async def scrape_cases(case_ids):
    return await asyncio.gather(*[CasePageScraper(case_id).scrape_case() for case_id in case_ids])


def parser_worker(q, worker_id):
    while True:
        cases = q.get()
        if cases == 'DONE':
            q.put('DONE')
            break
        try:
            # Get rid of None's
            filtered_cases = [case for case in cases if case]
            embedding_db.upsert_cases(filtered_cases)
            document_db.upsert_documents(filtered_cases)
            logging.info(f'{worker_id} - Upserted cases "{[case.id for case in filtered_cases]}".')
        except Exception:
            logging.exception(f'Parser #{worker_id} - Error while parsing cases:')


@periodic(FETCH_INTERVAL_IN_SECONDS)
async def periodic_fetch():
    await fetch_new_cases()

if __name__ == '__main__':
    asyncio.run(periodic_fetch())
