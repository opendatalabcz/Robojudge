from robojudge.components.scraping.ruling_scraper import RulingScraper
from robojudge.tasks.scraping_scheduler import (
    get_rulings_for_date,
)
from robojudge.db.mongo_db import document_db
from robojudge.utils.logger import logger
from robojudge.utils.settings import settings


async def initialize_dbs():
    logger.info("Initializing DBs with all previous rulings.")
    # Find the last fetch job for a date with at least one ruling published on that date
    last_fetched_date = (
        document_db.fetch_job_collection.find({"ruling_ids.0": {"$exists": True}})
        .sort("started_at", -1)
        .limit(1)
    )
    last_fetched_date = list(last_fetched_date)
    if len(last_fetched_date) > 0:
        start_date = list(last_fetched_date)[0]["date"]
    else:
        start_date = settings.FIRST_JUSTICE_DB_DATE

    dates = RulingScraper.get_ruling_dates_since_justice_db_start(start_date)
    for date in dates:
        await get_rulings_for_date(date)
