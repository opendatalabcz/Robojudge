import asyncio

from fastapi import FastAPI
import uvicorn

from scraper.case_page_scraper import CasePageScraper
from db.vector_db import DB

app = FastAPI()


# Milvus for vectors

# Basic POST endpoint for search and summary

# Background task for scraping

# MongoDB for metadata


# async def main():
#     db = DB()

#     db.create_collection('docs_1')

#     newest_id = await CasePageScraper.get_newest_case_id()
#     scraper = CasePageScraper(newest_id)
#     case = await scraper.scrape_case()

#     db.upsert_documents('docs_1', [case])

#     docs = db.get_documents('docs_1', [])
#     print(docs)


if __name__ == '__main__':
    uvicorn.run(app)
