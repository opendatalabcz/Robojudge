import datetime

import asyncio

import structlog
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import dramatiq
from robojudge.components.paginating_scraper import PaginatingScraper
from robojudge.utils.api_types import FetchCasesRequest
from robojudge.utils.functional import generate_uuid

from robojudge.utils.internal_types import Case, ScrapingJob, ScrapingJobStatus, ScrapingFilters, ScrapingJobType
from robojudge.utils.settings import settings
from robojudge.components.case_page_scraper import CasePageScraper
from robojudge.db.mongo_db import document_db
from robojudge.db.chroma_db import embedding_db
from robojudge.tasks.ruling_ids_selector import select_ruling_ids_for_scraping

BATCH_SIZE = 10
SCRAPER_THREAD_COUNT = 3
PARSER_PROCESS_COUNT = 3


logger: structlog.BoundLogger = structlog.get_logger()


if settings.ENABLE_SCRAPING:
    rabbitmq_broker = RabbitmqBroker(
        host=settings.RABBIT_HOST, port=settings.RABBIT_PORT)
    rabbitmq_broker.add_middleware(dramatiq.middleware.AsyncIO())

    dramatiq.set_encoder(dramatiq.PickleEncoder())
    dramatiq.set_broker(rabbitmq_broker)


def intialize_scheduled_scraping():
    scheduler = BlockingScheduler()
    scheduler.add_job(run_scraper_parser_pipeline,  CronTrigger.from_crontab(
        settings.SCRAPER_CRONTAB))

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


@dramatiq.actor(max_retries=settings.MAX_RETRIES, min_backoff=settings.MIN_BACKOFF, max_backoff=settings.MAX_BACKOFF)
async def scrape_ids_based_on_filter_worker(token: str, request: FetchCasesRequest):
    filters = ScrapingFilters(**request.filters.dict())
    scraping_job = ScrapingJob(token=token, filters=filters,
                               started_at=datetime.datetime.now(), type=ScrapingJobType.MANUAL)

    logger.info(f'Extracting ruling_ids based on this filter:',
                filters=filters)
    ruling_ids = await PaginatingScraper.extract_case_ids(filters)

    cases_in_db = document_db.collection.find({"case_id": {"$in": ruling_ids}})
    for db_case in cases_in_db:
        ruling_ids.remove(db_case["case_id"])

    if request.limit:
        ruling_ids = ruling_ids[: request.limit]

    scraping_job.filtered_ruling_ids = ruling_ids
    scraping_job.last_ruling_id = scraping_job.filtered_ruling_ids[-1] if len(
        scraping_job.filtered_ruling_ids) else -1

    return scraping_job


@dramatiq.actor(max_retries=settings.MAX_RETRIES, min_backoff=settings.MIN_BACKOFF, max_backoff=settings.MAX_BACKOFF)
async def scraper_worker(scraping_job: ScrapingJob = None):
    if not scraping_job:
        scraping_job = ScrapingJob(
            token=generate_uuid(), started_at=datetime.datetime.now())

        scraping_job.filtered_ruling_ids = await select_ruling_ids_for_scraping()
        scraping_job.last_ruling_id = scraping_job.filtered_ruling_ids[-1] if len(
            scraping_job.filtered_ruling_ids) else -1

    document_db.scraping_job_collection.replace_one({'token': scraping_job.token},
                                                    scraping_job.dict(),
                                                    upsert=True
                                                    )

    logger.info(
        f'Initializing scraping for ruling_ids:', ruling_ids=scraping_job.filtered_ruling_ids)

    scraped_rulings = await asyncio.gather(
        *[CasePageScraper(ruling_id).scrape_case() for ruling_id in scraping_job.filtered_ruling_ids]
    )

    return scraping_job, scraped_rulings


@dramatiq.actor(max_retries=settings.MAX_RETRIES, min_backoff=settings.MIN_BACKOFF, max_backoff=settings.MAX_BACKOFF)
def parser_worker(args):
    """
    Takes scraped rulings and upserts them into DBs.
    """
    try:
        scraping_job, rulings = args
        scraped_rulings: list[Case] = [ruling for ruling in rulings if ruling]
        scraped_ruling_ids = [ruling.case_id for ruling in scraped_rulings]

        embedding_db.upsert_cases(scraped_rulings)
        document_db.upsert_documents(scraped_rulings)

        document_db.scraping_job_collection.update_one(
            {'token': scraping_job.token}, {"$set": {'finished_at': datetime.datetime.now(), 'status': ScrapingJobStatus.FINISHED, 'scraped_ruling_ids': scraped_ruling_ids}})

        logger.info(
            f'Scraped and parsed rulings with ids:', ruling_ids=scraped_ruling_ids
        )
    except Exception:
        logger.exception(
            f"Error while parsing rulings:")


run_scraper_parser_pipeline = dramatiq.pipeline(
    [scraper_worker.message(), parser_worker.message()]).run

run_filtered_scraper_parser_pipeline = dramatiq.pipeline(
    [scrape_ids_based_on_filter_worker.message(), scraper_worker.message(), parser_worker.message()]).run
