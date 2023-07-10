import asyncio

from fastapi import FastAPI
import uvicorn

from utils.logger import logging
from scraper.case_page_scraper import CasePageScraper
from server.db.chroma_db import embedding_db
from db.mongo_db import test_db
import routers.query

app = FastAPI()

app.include_router(routers.query.router)


# MongoDB for metadata
# Full DB case upload method

# Basic POST endpoint for search and summary

# Background task for scraping


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
    # uvicorn.run(app, port=4000)

    # logging.info(embedding_db.client.heartbeat())

    col = test_db.test_collection

    id = col.insert_one({
        "title": 'whatever'
    })

    print(id)
