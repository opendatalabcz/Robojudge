from robojudge.utils.settings import settings
from robojudge.components.case_page_scraper import CasePageScraper
from robojudge.db.mongo_db import document_db


def get_ruling_ids_ascending(latest_web_id: int, latest_id_in_db: int, ruling_ids_in_db: set) -> list:
    upper = min(latest_id_in_db +
                settings.SCRAPER_SINGLE_RUN_CASE_COUNT + 1, latest_web_id)
    lower = latest_id_in_db + 1

    return sorted(set(range(lower, upper)).difference(ruling_ids_in_db), key=int)


def get_ruling_ids_descending(latest_web_id: int, ruling_ids_in_db: set) -> list:
    # Max is set to latest_web_id, we have to find min
    to_be_scraped_case_ids = set(
        range(latest_web_id, latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1))

    to_be_scraped_case_ids.difference_update(ruling_ids_in_db)
    if not len(to_be_scraped_case_ids):
        to_be_scraped_case_ids.add(
            latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT)

    lowest_case_id = min(to_be_scraped_case_ids)
    while len(to_be_scraped_case_ids) < settings.SCRAPER_SINGLE_RUN_CASE_COUNT:
        for i in range(lowest_case_id - 1, lowest_case_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1):
            lowest_case_id = i
            to_be_scraped_case_ids.add(lowest_case_id)

        to_be_scraped_case_ids.difference_update(ruling_ids_in_db)

    ruling_ids_in_correct_batch_size = sorted(to_be_scraped_case_ids, key=int, reverse=True)[
        :settings.SCRAPER_SINGLE_RUN_CASE_COUNT]

    if lowest_case_id <= settings.OLDEST_KNOWN_CASE_ID:
        ruling_ids_in_correct_batch_size = list(filter(
            lambda id: id >= settings.OLDEST_KNOWN_CASE_ID, ruling_ids_in_correct_batch_size))

    return ruling_ids_in_correct_batch_size


async def select_ruling_ids_for_scraping() -> set:
    latest_web_id = await CasePageScraper.get_newest_case_id()
    latest_id_in_db = document_db.find_latest_case_id() or settings.OLDEST_KNOWN_CASE_ID

    ruling_ids_in_db = list(document_db.collection.find({}, {"case_id"}))
    ruling_ids_in_db = set(int(case["case_id"]) for case in ruling_ids_in_db)

    if settings.SCRAPE_CASES_FROM_LAST:
        return get_ruling_ids_descending(latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)
    else:
        return get_ruling_ids_ascending(latest_web_id=latest_web_id, latest_id_in_db=latest_id_in_db, ruling_ids_in_db=ruling_ids_in_db)
