import json

import pytest
from bs4 import BeautifulSoup

from robojudge.components.case_page_scraper import CasePageScraper


@pytest.fixture(scope="session")
def html_page():
    with open("tests/assets/page.html", "r") as rf:
        return rf.read()


@pytest.fixture(scope="session")
def case_scraper(html_page: str):
    scraper = CasePageScraper("435673")
    scraper.page = html_page
    scraper.page_soup = BeautifulSoup(scraper.page, "html.parser")
    return scraper


@pytest.fixture(scope="session")
def parsed_case():
    with open('tests/assets/scraped_case.json', 'r') as rf:
        return json.load(rf)


@pytest.mark.asyncio
async def test_scrape_case_page(html_page: str):
    tested_page = await CasePageScraper("435673").scrape_case_page()
    assert tested_page == html_page


def test_extract_metadata(case_scraper: CasePageScraper, parsed_case: dict):
    # Compare JSON because of special field type like datetime.datetime()
    assert case_scraper.extract_metadata().json() == json.dumps(parsed_case["metadata"])


def test_extract_text(case_scraper: CasePageScraper, parsed_case: dict):
    verdict, reasoning = case_scraper.extract_text()
    assert verdict == parsed_case["verdict"]
    assert reasoning == parsed_case["reasoning"]
