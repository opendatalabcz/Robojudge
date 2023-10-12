import logging
import asyncio

from playwright.async_api import (
    async_playwright,
    Page,
)

from robojudge.components.case_page_scraper import CasePageScraper
from robojudge.utils.internal_types import CaseFetchJob, CaseFetchJobStatus
from robojudge.utils.settings import settings
from robojudge.db.mongo_db import document_db
from robojudge.tasks.case_scraping import run_scraping_instance
from robojudge.utils.logger import logging
from robojudge.utils.internal_types import ScrapingFilters
from robojudge.utils.api_types import FetchCasesRequest

logger = logging.getLogger(__name__)


class PaginatingScraper:
    MAX_SCAPE_SIZE = 2000

    @classmethod
    async def run_fetch_job(cls, token: str, request: FetchCasesRequest):
        try:
            filters = ScrapingFilters(**request.filters.dict())
            fetch_job = CaseFetchJob(token=token, filters=filters)

            document_db.fetch_job_collection.insert_one(
                fetch_job.dict()
            )
            logger.info(f'Start extracting case_ids for token "{token}".')

            case_ids = await cls.extract_case_ids(filters)

            cases_in_db = document_db.collection.find({"case_id": {"$in": case_ids}})
            all_case_ids = case_ids[:]
            for db_case in cases_in_db:
                case_ids.remove(db_case["case_id"])

            if request.limit:
                case_ids = case_ids[: request.limit]

            # TODO: embedding and stuff should be done separately ...
            if len(case_ids):
                logger.info(
                    f'Starting scraping missing cases for token "{token}": {case_ids}'
                )
                await run_scraping_instance(case_ids)

            document_db.fetch_job_collection.find_one_and_update(
                {"token": token},
                {
                    "$set": {
                        "case_ids": all_case_ids,
                        "status": CaseFetchJobStatus.FINISHED.value,
                    }
                },
            )
            logger.info(f'Finished scraping cases for token "{token}".')
        except Exception:
            logger.exception(f'Error while processing fetch job for token "{token}":')
            document_db.fetch_job_collection.find_one_and_update(
                {"token": token},
                {
                    "$set": {
                        "status": CaseFetchJobStatus.FINISHED.value,
                    }
                },
            )

    @classmethod
    async def extract_case_ids(cls, filters: ScrapingFilters) -> list[str]:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()

            await cls.apply_filters_on_main_page(page, filters)

            case_ids = []

            is_next_button_enabled = True
            while (
                is_next_button_enabled
                and len(case_ids) <= PaginatingScraper.MAX_SCAPE_SIZE
            ):
                case_ids.extend(await cls.extract_case_links_from_page(page))
                is_next_button_enabled = await cls.navigate_forward(page)

            return case_ids

    @classmethod
    async def apply_filters_on_main_page(cls, page, filters: ScrapingFilters):
        # Disable timeout by setting it to 0
        await page.goto(url=CasePageScraper.MAIN_PAGE_URL, timeout=0)

        await cls.input_filter_values(page, filters)

        search_button = page.locator(
            'button[class="btn btn-primary mx-1 my-2"]',
        )
        await search_button.click()

        await page.wait_for_selector(
            'table[class="table table-striped dataTable bg-white rounded"]',
        )

    @classmethod
    async def input_filter_values(cls, page: Page, filters: ScrapingFilters):
        await page.get_by_placeholder("(hledaná slova)").fill(filters.fulltext_search)

        await page.get_by_placeholder("(Vyhledat soud)").fill(filters.court)

        await page.get_by_placeholder("(jméno)").fill(filters.judge_firstname)
        await page.get_by_placeholder("(příjmení)").fill(filters.judge_lastname)

        inputs = (
            await page.get_by_text("Datum vydání (od - do):")
            .locator("..")
            .locator("input")
            .all()
        )

        if len(inputs) == 2:
            await inputs[0].fill(filters.publication_date_from, force=True)
            await inputs[1].fill(filters.publication_date_to)

    @classmethod
    async def navigate_forward(cls, page: Page) -> bool:
        next_button = page.locator("li").filter(has_text="Další")
        if not await next_button.count():
            return False

        next_button_classes = await next_button.get_attribute("class")
        if "disabled" in next_button_classes:
            return False

        await page.locator("li").filter(has_text="Další").click()
        await page.wait_for_selector(
            'table[class="table table-striped dataTable bg-white rounded"]'
        )
        return True

    @classmethod
    async def extract_case_links_from_page(cls, page: Page):
        links = await page.locator("tr").filter(has=page.locator("a")).all()

        case_ids = []
        for link in links:
            case_id = await link.locator("a").get_attribute("href")
            case_ids.append(case_id.removeprefix(CasePageScraper.LINK_PREFIX))

        return case_ids


if __name__ == "__main__":
    asyncio.run(
        PaginatingScraper.extract_case_ids(
            ScrapingFilters(judge_firstname="Petr", publication_date_from="2023-09-30")
        )
    )
