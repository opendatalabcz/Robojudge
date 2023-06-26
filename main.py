import asyncio

from fastapi import FastAPI

from scraper.case_page_scraper import CasePageScraper

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def main():
    # print(await CasePageScraper.get_newest_case_id())
    scraper = CasePageScraper('434189')
    case = await scraper.scrape_case()
    print(case.metadata)


if __name__ == '__main__':
    asyncio.run(main())
