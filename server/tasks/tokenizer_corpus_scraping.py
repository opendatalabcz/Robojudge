import asyncio
import random
from pathlib import Path

import more_itertools
from concurrent.futures import ProcessPoolExecutor

from server.utils.settings import settings
from server.scraper.case_page_scraper import CasePageScraper
from server.utils.logger import logging

FETCH_INTERVAL_IN_SECONDS = 3600
BATCH_SIZE = 20
SAMPLE_SIZE = 20
SCRAPER_PROCESS_COUNT = 3
OUTPUT_PATH = Path('datasets/tokenizer/')


async def determine_case_ids_to_parse(sample_size):
    latest_id = await CasePageScraper.get_newest_case_id()

    return random.choices(range(settings.OLDEST_KNOWN_CASE_ID, latest_id+1), k=sample_size)


async def scrape_corpus(sample_size=SAMPLE_SIZE):
    case_ids = await determine_case_ids_to_parse(sample_size)

    # Scraping is IO bound (waiting for the network to return), so asyncio with threads is enough
    case_id_chunks = more_itertools.chunked(case_ids, BATCH_SIZE)
    with ProcessPoolExecutor(max_workers=SCRAPER_PROCESS_COUNT) as executor:
        for result in executor.map(scraper_worker, case_id_chunks):
            for scraped_case in result:
                if scraped_case is not None:
                    logging.info(
                        f'Writing reasoning of case "{scraped_case.id}" to "{OUTPUT_PATH}".')
                    Path(OUTPUT_PATH /
                         scraped_case.id).with_suffix('.txt').write_text(scraped_case.reasoning)

    logging.info('All provided case_ids scraped.')


def scraper_worker(case_ids):
    """Has to be wrapped because of its async nature
    """
    return asyncio.run(scrape_cases(case_ids))


async def scrape_cases(case_ids):
    return await asyncio.gather(*[CasePageScraper(case_id).scrape_case() for case_id in case_ids])

if __name__ == '__main__':
    asyncio.run(scrape_corpus(20))
