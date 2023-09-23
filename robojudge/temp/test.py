import asyncio

from robojudge.db.chroma_db import embedding_db
from robojudge.db.mongo_db import document_db
from robojudge.components.scraper.case_page_scraper import CasePageScraper

# https://rozhodnuti.justice.cz/rozhodnuti/435673


async def main():
    case = await CasePageScraper(435673).scrape_case()

    embedding_db.upsert_cases([case])
    await document_db.upsert_documents([case])

if __name__ == '__main__':
    asyncio.run(main())
