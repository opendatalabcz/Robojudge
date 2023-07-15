import asyncio

from server.db.chroma_db import embedding_db
# from server.db.mongo_db import metadata_db
# from server.model.embedding import embedder
from server.scraper.case_page_scraper import CasePageScraper
from server.utils.types import Case

from server.tasks.fetch_new_cases import fetch_new_cases

# https://rozhodnuti.justice.cz/rozhodnuti/435673


async def main():
    case = await CasePageScraper(435673).scrape_case()
    # case2 = await CasePageScraper(435671).scrape_case()

    embedding_db.upsert_cases([case])
    # metadata_db.upsert_metadata([case, case2])

    # await fetch_new_cases()

if __name__ == '__main__':
    asyncio.run(main())
