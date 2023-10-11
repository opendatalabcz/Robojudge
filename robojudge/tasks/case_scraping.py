import datetime

import asyncio
import uvicorn
from multiprocessing import Queue, Process
from concurrent.futures import ThreadPoolExecutor

import more_itertools
from rocketry import Rocketry

from robojudge.utils.internal_types import Case, ScrapingInformation
from robojudge.utils.settings import settings
from robojudge.db.chroma_db import embedding_db
from robojudge.db.mongo_db import document_db
from robojudge.components.case_page_scraper import CasePageScraper
from robojudge.db.mongo_db import document_db
from robojudge.utils.logger import logging

BATCH_SIZE = 10
SCRAPER_THREAD_COUNT = 3
PARSER_PROCESS_COUNT = 3


logger = logging.getLogger(__name__)


async def determine_case_ids_to_parse():
    latest_id = await CasePageScraper.get_newest_case_id()
    latest_id_in_db = document_db.find_latest_case_id() or settings.OLDEST_KNOWN_CASE_ID

    case_ids_in_db = list(document_db.collection.find({}, {"case_id"}))
    case_ids_in_db = set(int(case["case_id"]) for case in case_ids_in_db)

    lower = latest_id_in_db + 1
    upper = min(latest_id_in_db + settings.SCRAPER_MAX_RUN_CASE_COUNT, latest_id) + 1

    return sorted(set(range(lower, upper)).difference(case_ids_in_db), key=int)


app = Rocketry()


LAST_SCRAPING_EMPTY = False


@app.cond("last_scraping_empty")
def last_scraping_empty():
    return LAST_SCRAPING_EMPTY


@app.task(
    f"last_scraping_empty | every {settings.SCRAPER_TASK_INTERVAL_IN_SECONDS} seconds"
)
async def run_scraping_instance(case_ids: list[str] = None):
    if not case_ids:
        case_ids = await determine_case_ids_to_parse()

    q = Queue()

    # Parsers are computation-intensive so separate processes are required
    parsers = []
    for index in range(PARSER_PROCESS_COUNT):
        parser = Process(target=parser_worker, args=(q, index))
        parser.start()
        parsers.append(parser)

    unsuccessful_case_count = 0
    # Scraping is IO bound (waiting for the network to return), so asyncio with threads is enough
    case_id_chunks = more_itertools.chunked(case_ids, BATCH_SIZE)
    with ThreadPoolExecutor(
        max_workers=SCRAPER_THREAD_COUNT, thread_name_prefix="scraper"
    ) as executor:
        coroutines = [
            (scrape_cases(chunk), index) for index, chunk in enumerate(case_id_chunks)
        ]
        for index, result in enumerate(executor.map(scraper_worker, coroutines)):
            # Get rid of None's
            filtered_cases: list[Case] = [case for case in result if case]

            logger.info(
                f"Finished scraping case batch #{index} ({len(filtered_cases)}/{len(result)})"
            )
            q.put(filtered_cases)
            unsuccessful_case_count += len(result) - len(filtered_cases)

    q.put("DONE")

    for parser in parsers:
        parser.join()

    scraping_information = ScrapingInformation(
        last_case_id=case_ids[-1],
        timestamp=datetime.datetime.now(),
        unsuccessful_case_count=unsuccessful_case_count,
    )
    document_db.insert_scraping_instance_information(scraping_information)

    global LAST_SCRAPING_EMPTY
    if len(case_ids) == unsuccessful_case_count:
        logger.warning(f"No case_ids fetched, repeating task immediately.")
        LAST_SCRAPING_EMPTY = True
    else:
        logger.info(
            f"Fetched {(len(case_ids) - unsuccessful_case_count)}/{len(case_ids)} case_ids."
        )
        LAST_SCRAPING_EMPTY = False


# Has to be wrapped because of its async nature
def scraper_worker(params):
    coroutine, batch_id = params
    logger.info(f"Initializing case batch #{batch_id}")
    return asyncio.run(coroutine)


async def scrape_cases(case_ids):
    return await asyncio.gather(
        *[CasePageScraper(case_id).scrape_case() for case_id in case_ids]
    )


def parser_worker(q, worker_id):
    while True:
        cases = q.get()
        if cases == "DONE":
            q.put("DONE")
            break
        try:
            embedding_db.upsert_cases(cases)
            document_db.upsert_documents(cases)
            logger.info(
                f'{worker_id} - Upserted cases "{[case.case_id for case in cases]}".'
            )
        except Exception:
            logger.exception(f"Parser #{worker_id} - Error while parsing cases:")


async def create_scheduler_async_task():
    scheduled = asyncio.create_task(app.serve())

    await scheduled


def run_scheduler():
    asyncio.run(create_scheduler_async_task())


if __name__ == "__main__":
    run_scheduler()
