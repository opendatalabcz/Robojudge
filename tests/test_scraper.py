import json

import httpx
import pytest

from robojudge.components.scraping.ruling_scraper import RulingScraper


@pytest.fixture(scope="session")
def fetched_ruling_infos():
    with open("tests/assets/fetched_ruling_infos.json", "r") as rf:
        return json.load(rf)


@pytest.fixture(scope="session")
def fetched_ruling_info(fetched_ruling_infos: list[dict]):
    return fetched_ruling_infos[0]


@pytest.fixture(scope="session")
def fetched_ruling():
    with open("tests/assets/fetched_ruling.json", "r") as rf:
        ruling_json = json.load(rf)
        return ruling_json


@pytest.mark.asyncio
async def test_get_ruling_infos_for_date(fetched_ruling_infos: list[dict]):
    DATE = "2024/02/04"

    ruling_infos = await RulingScraper.get_ruling_infos_for_date(DATE)

    assert len(ruling_infos) == 2
    assert ruling_infos == fetched_ruling_infos


@pytest.mark.asyncio
async def test_get_ruling_infos_for_empty_date():
    EMPTY_DATE = "2024-02-03"
    ruling_infos = await RulingScraper.get_ruling_infos_for_date(EMPTY_DATE)

    assert ruling_infos == []


@pytest.mark.asyncio
async def test_get_ruling_infos_with_multiple_pages():
    DATE = "2024-02-01"
    ruling_infos = await RulingScraper.get_ruling_infos_for_date(DATE)

    assert len(ruling_infos) == 279


@pytest.mark.asyncio
async def test_get_ruling_by_url(fetched_ruling: str, fetched_ruling_info: dict):
    # Compare JSON because of special field type like datetime.datetime()
    async with httpx.AsyncClient() as client:
        tested_ruling, _ = await RulingScraper.get_ruling_by_url(
            fetched_ruling_info, client
        )

        assert json.loads(tested_ruling.json()) == fetched_ruling


def test_get_ruling_dates_since_justice_db_start():
    start_date = "2024-02-27"
    end_date = "2024-03-02"

    dates = RulingScraper.get_ruling_dates_since_justice_db_start(start_date, end_date)

    assert dates == ["2024-02-28", "2024-02-29", "2024-03-01"]
