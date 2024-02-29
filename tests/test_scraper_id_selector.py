# TODO: mock playwright call to l atest
# TODO: mock cases from Mongo

from robojudge.utils.settings import settings
from robojudge.tasks.case_scraping import get_ruling_ids_ascending, get_ruling_ids_descending


def test_ascending_order_empty_db():
    latest_id_in_db = settings.OLDEST_KNOWN_CASE_ID
    latest_web_id = 3334

    ruling_ids = get_ruling_ids_ascending(
        latest_web_id=latest_web_id, latest_id_in_db=latest_id_in_db, ruling_ids_in_db=set())

    assert set(ruling_ids) == set(list(range(settings.OLDEST_KNOWN_CASE_ID + 1,
                                             settings.OLDEST_KNOWN_CASE_ID + settings.SCRAPER_SINGLE_RUN_CASE_COUNT + 1)))


def test_ascending_order_non_empty_db():
    latest_id_in_db = 654
    latest_web_id = 3334

    ruling_ids = get_ruling_ids_ascending(
        latest_web_id=latest_web_id, latest_id_in_db=latest_id_in_db, ruling_ids_in_db=set())

    assert set(ruling_ids) == set(list(range(latest_id_in_db + 1,
                                             latest_id_in_db + settings.SCRAPER_SINGLE_RUN_CASE_COUNT + 1)))


def test_descending_order_empty_db():
    latest_web_id = 3334

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=set())

    assert set(ruling_ids) == set(list(range(latest_web_id,
                                             latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1)))


def test_descending_order_continuing_from_db():
    latest_web_id = 600

    ruling_ids_in_db = set(
        range(latest_web_id, latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1))

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)

    assert set(ruling_ids) == set(list(range(latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT,
                                             latest_web_id - 2 * settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1)))


def test_descending_order_continuing_from_db_some_ids_missing():
    latest_web_id = 700

    ruling_ids_in_db = set(
        range(latest_web_id, latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1))

    non_existent_ids = [699, 698]
    for id in non_existent_ids:
        ruling_ids_in_db.remove(id)

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)

    assert set(ruling_ids) == set([*non_existent_ids, *list(range(latest_web_id - settings.SCRAPER_SINGLE_RUN_CASE_COUNT,
                                                                  latest_web_id - (2 * settings.SCRAPER_SINGLE_RUN_CASE_COUNT - 2), -1))])


def test_descending_order_newest_web_id_and_continuing_from_db():
    latest_web_id = 702

    latest_in_in_db = latest_web_id - 2
    ruling_ids_in_db = set(
        range(latest_in_in_db, latest_in_in_db - settings.SCRAPER_SINGLE_RUN_CASE_COUNT, -1))

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)

    assert set(ruling_ids) == set([*list(range(latest_web_id, latest_web_id - 2, -1)), *list(range(latest_in_in_db - settings.SCRAPER_SINGLE_RUN_CASE_COUNT,
                                                                                                   latest_in_in_db - (2 * settings.SCRAPER_SINGLE_RUN_CASE_COUNT - 2), -1))])


def test_descending_order_reached_oldest_case_id():
    latest_web_id = 800

    latest_in_in_db = settings.OLDEST_KNOWN_CASE_ID + 3
    ruling_ids_in_db = set(
        range(latest_web_id, latest_in_in_db, -1))

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)

    assert set(ruling_ids) == set(
        list(range(latest_in_in_db, settings.OLDEST_KNOWN_CASE_ID - 1, -1)))


def test_descending_order_performance():
    latest_web_id = 1_000_000

    latest_in_in_db = settings.OLDEST_KNOWN_CASE_ID + 3
    ruling_ids_in_db = set(
        range(latest_web_id, latest_in_in_db, -1))

    ruling_ids = get_ruling_ids_descending(
        latest_web_id=latest_web_id, ruling_ids_in_db=ruling_ids_in_db)

    assert set(ruling_ids) == set(
        list(range(latest_in_in_db, settings.OLDEST_KNOWN_CASE_ID - 1, -1)))
