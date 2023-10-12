import pytest
from playwright.async_api import async_playwright, Page, expect

from robojudge.components.paginating_scraper import PaginatingScraper
from robojudge.components.case_page_scraper import CasePageScraper
from robojudge.utils.internal_types import ScrapingFilters

# Playwright async cannot be currently tested with pytest: https://github.com/microsoft/playwright-pytest/issues/74


@pytest.mark.skip(reason="Playwright async is untestable right now.")
@pytest.mark.asyncio
async def test_input_filters(page: Page):
    filters = ScrapingFilters(
        fulltext_search="slovo",
    )

    await page.goto(url=CasePageScraper.MAIN_PAGE_URL, timeout=0)

    await PaginatingScraper.input_filter_values(page, filters)

    expect(await page.get_by_placeholder("(hledaná slova)")).to_contain_text("slovo")


@pytest.mark.skip(reason="Playwright async is untestable right now.")
@pytest.mark.asyncio
async def test_single_page_results(page: Page):
    filters = ScrapingFilters(
        judge_firstname="Petr",
        judge_lastname="Blažej",
        publication_date_from="2023-05-12",
        publication_date_to="2023-05-19",
    )

    await PaginatingScraper.apply_filters_on_main_page(page, filters)

    case_ids = await PaginatingScraper.extract_case_links_from_page(page)

    assert case_ids == ["454489", "449564"]


@pytest.mark.skip(reason="Playwright async is untestable right now.")
@pytest.mark.asyncio
async def test_multiple_page_results(page: Page):
    filters = ScrapingFilters(
        judge_firstname="Petr",
        publication_date_from="2023-05-12",
        publication_date_to="2023-05-16",
    )

    case_ids = await PaginatingScraper.extract_case_ids(filters)

    assert len(case_ids) > 0

    await PaginatingScraper.apply_filters_on_main_page(page, filters)

    case_ids = await PaginatingScraper.extract_case_links_from_page(page)

    assert case_ids == [
        "455215",
        "454489",
        "451290",
        "448706",
        "448689",
        "448574",
        "445623",
        "444388",
        "443416",
        "442658",
        "442656",
        "442628",
        "442445",
        "442164",
        "441888",
        "441884",
        "440070",
        "439558",
        "439273",
        "438537",
        "438529",
        "438002",
        "437926",
        "437925",
        "437924",
        "437798",
        "437786",
        "437691",
        "437121",
        "436322",
        "435660",
        "434450",
        "434367",
        "434186",
        "434162",
        "434055",
        "433435",
        "432555",
        "432554",
        "432424",
        "431514",
        "430779",
        "430261",
        "429820",
        "429452",
        "429446",
        "425328",
    ]
