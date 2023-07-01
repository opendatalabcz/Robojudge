import asyncio

from server.model.embedding import embedder
from server.scraper.case_page_scraper import CasePageScraper

# https://rozhodnuti.justice.cz/rozhodnuti/435673

async def main():
    # newest_id = await CasePageScraper.get_newest_case_id()
    scraper = CasePageScraper(435673)
    case = await scraper.scrape_case()
    print(case.verdict)
    print('====')
    print(case.reasoning)


if __name__ == '__main__':
    asyncio.run(main())
