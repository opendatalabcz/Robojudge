import re
import logging

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from server.utils.settings import settings
from server.utils.types import DOCUMENT_METADATA_MAP, Case, Metadata, CaseMetadataAttributes
from server.utils.logger import logging
from server.utils.functional import parse_date

logger = logging.getLogger(__name__)


class CasePageScraper:
    JUSTICE_BASE_URL = 'https://rozhodnuti.justice.cz/rozhodnuti/'
    MAIN_PAGE_URL = "https://rozhodnuti.justice.cz/SoudniRozhodnuti/"
    LINK_PREFIX = 'rozhodnuti/'
    JEDNACI_CISLO_REGEX = r'(\d+\s\w{1,3}\s\d+\/\d{4,}(-\d+)?)'

    case_id: str = ''
    page: str = ''
    page_soup: BeautifulSoup

    def __init__(self, case_id: str | int) -> None:
        self.case_id = str(case_id)

    async def scrape_case(self) -> Case | None:
        try:
            self.page = await CasePageScraper.scrape_case_page(self.case_id)
            if not self.page:
                return None
            
            self.page_soup = BeautifulSoup(self.page, 'html.parser')

            verdict, reasoning = self.extract_text()
            metadata = self.extract_metadata()

            logging.debug(f'Scraped case: {self.case_id}')

            return Case(id=self.case_id, verdict=verdict, reasoning=reasoning, metadata=metadata)
        except Exception:
            logging.exception(f'Error while scraping case "{self.case_id}":')

    async def scrape_case_page(self):
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()
            await page.goto(CasePageScraper.JUSTICE_BASE_URL + self.case_id)

            try:
                await page.wait_for_selector('div[id="PrintDiv"]', timeout=settings.SCRAPER_TIMEOUT)
            except PlaywrightTimeoutError:
                logging.warning(f'Timeout or no case with {self.case_id}.')
                return ''

            return await page.content()

    def extract_metadata(self):
        rows = self.page_soup.find_all(name='dl')
        metadata = {}
        for row in rows:
            key = row.find('dt').get_text().replace(':', '')
            val = row.find('dd').get_text(', ', strip=True)
            try:
                snake_case_key = DOCUMENT_METADATA_MAP[key]
            except:
                logger.warning(f'Unknown metadata key "{key}"')
                snake_case_key = key
            metadata[snake_case_key] = val

        metadata[CaseMetadataAttributes.SENTENCE_DATE] = parse_date(
            metadata[CaseMetadataAttributes.SENTENCE_DATE])

        metadata[CaseMetadataAttributes.PUBLICATION_DATE] = parse_date(
            metadata[CaseMetadataAttributes.PUBLICATION_DATE])

        if metadata.get(CaseMetadataAttributes.KEYWORDS, None):
            metadata[CaseMetadataAttributes.KEYWORDS] = metadata[CaseMetadataAttributes.KEYWORDS].split(
                ', ')

        metadata[CaseMetadataAttributes.REGULATIONS_MENTIONED] = metadata[CaseMetadataAttributes.REGULATIONS_MENTIONED].split(
            ', ')

        if metadata.get(CaseMetadataAttributes.RELATED_CASES, None):
            metadata[CaseMetadataAttributes.RELATED_CASES] = self.parse_related_cases(
                metadata[CaseMetadataAttributes.RELATED_CASES])
        else:
            metadata[CaseMetadataAttributes.RELATED_CASES] = []

        return Metadata(**metadata)

    def extract_text(self) -> tuple[str, str]:
        text_box = self.page_soup.find(name='div', class_='detailBottom')
        rows = text_box.find_all(name='p')
        texts = [row.get_text() for row in rows]

        verdict_index = texts.index('takto:')
        reasoning_index = texts.index('Odůvodnění:')
        footer_index = texts.index('Poučení:')

        verdict = '\n'.join(texts[verdict_index+1: reasoning_index])
        reasoning = '\n'.join(texts[reasoning_index+1: footer_index])

        return verdict, reasoning

    def parse_related_cases(self, raw_related_cases: str) -> list[str]:
        matches = re.compile(self.JEDNACI_CISLO_REGEX).findall(
            raw_related_cases)
        return [match[0] for match in matches]

    @staticmethod
    async def get_newest_case_id():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()
            await page.goto(CasePageScraper.MAIN_PAGE_URL)

            search_button = page.locator(
                'button[class="btn btn-primary mx-1 my-2"]')
            await search_button.click()

            await page.wait_for_selector(
                'table[class="table table-striped dataTable bg-white rounded"]')

            links = await page.locator('tr').filter(has=page.locator('a')).all()

            case_ids = []
            for link in links:
                case_id = await link.locator('a').get_attribute('href')
                case_ids.append(case_id.removeprefix(
                    CasePageScraper.LINK_PREFIX))

            return int(case_ids[0])
