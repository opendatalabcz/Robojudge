import datetime

import asyncio

import httpx
import more_itertools
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import dramatiq

from robojudge.components.scraping.ruling_scraper import RulingScraper
from robojudge.utils.functional import extract_ruling_id
from robojudge.utils.internal_types import (
    FetchJob,
    Ruling,
)
from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.db.mongo_db import document_db
from robojudge.db.chroma_db import embedding_db

rabbitmq_broker = RabbitmqBroker(host=settings.RABBIT_HOST, port=settings.RABBIT_PORT)
rabbitmq_broker.add_middleware(dramatiq.middleware.AsyncIO())
rabbitmq_broker.add_middleware(dramatiq.middleware.Pipelines())

dramatiq.set_encoder(dramatiq.PickleEncoder())
dramatiq.set_broker(rabbitmq_broker)


def intialize_scheduled_scraping():
    """
    Schedules the requested number of parallel scrapers.
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(
        get_ruling_for_yesterday,
        CronTrigger.from_crontab(settings.SCRAPER_CRONTAB),
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


def get_ruling_for_yesterday():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=60)
    construct_fetch_upsert_pipeline(yesterday).run()


async def get_rulings_for_date(date: str):
    """
    Returns basic information about all rulings published on the provided date.S
    """
    logger.info("Fetching ruling_ids for date:", date=date)
    ruling_infos = await RulingScraper.get_ruling_infos_for_date(date)

    fetch_job = FetchJob(
        date=date,
        started_at=datetime.datetime.now(),
    )

    document_db.fetch_job_collection.replace_one(
        {"date": fetch_job.date}, fetch_job.dict(), upsert=True
    )

    for ruling_info_batch in more_itertools.chunked(
        ruling_infos, settings.SCRAPER_SINGLE_RUN_CASE_COUNT
    ):
        construct_fetch_upsert_pipeline(ruling_info_batch).run()


FETCH_JOB_INTERVAL = settings.BASE_FETCH_JOB_INTERVAL


@dramatiq.actor(max_retries=settings.MAX_RETRIES, queue_name="fetching-queue")
async def fetch_worker(ruling_infos: list[dict]):
    """
    Fetches all data about given rulings.
    """
    ruling_ids = [
        extract_ruling_id(ruling_info.get("odkaz", "")) for ruling_info in ruling_infos
    ]

    logger.info(f"Fetching ({len(ruling_infos)}) rulings:", ruling_ids=ruling_ids)

    async with httpx.AsyncClient(timeout=60) as client:
        scraped_rulings = await asyncio.gather(
            *[
                RulingScraper.get_ruling_by_url(ruling_info=ruling_info, client=client)
                for ruling_info in ruling_infos
            ]
        )

    failed_ruling_infos = []
    successful_rulings: list[Ruling] = []
    for scraped_ruling, ruling_info in scraped_rulings:
        if scraped_ruling:
            successful_rulings.append(scraped_ruling)
        else:
            failed_ruling_infos.append(ruling_info)

    successful_ruling_ids = [ruling.ruling_id for ruling in successful_rulings]
    logger.info(
        f"Fetched ({len(successful_rulings)}) rulings:",
        ruling_ids=successful_ruling_ids,
    )

    global FETCH_JOB_INTERVAL
    if len(failed_ruling_infos):
        failed_ruling_ids = [
            extract_ruling_id(ruling_info.get("odkaz", ""))
            for ruling_info in failed_ruling_infos
        ]
        logger.info(
            f"Repeating scraping for ({len(failed_ruling_ids)}) failed ruling_infos:",
            ruling_ids=failed_ruling_ids,
        )
        FETCH_JOB_INTERVAL += settings.FAILED_FETCH_JOB_INTERVAL_INCREASE
        logger.info(f"FETCH_JOB_INTERVAL is now {FETCH_JOB_INTERVAL} s.")
        construct_fetch_upsert_pipeline(failed_ruling_infos).run()
    else:
        previous_interval = FETCH_JOB_INTERVAL
        FETCH_JOB_INTERVAL = max(
            settings.BASE_FETCH_JOB_INTERVAL,
            FETCH_JOB_INTERVAL - settings.SUCCESSFUL_FETCH_JOB_INTERVAL_INCREASE,
        )
        if previous_interval != FETCH_JOB_INTERVAL:
            logger.info(f"FETCH_JOB_INTERVAL is now {FETCH_JOB_INTERVAL} s.")

    # Enforced wait not to overburden the justice API (which has rate limiting and would block further requests)
    await asyncio.sleep(FETCH_JOB_INTERVAL)

    return successful_rulings


@dramatiq.actor(max_retries=settings.MAX_RETRIES, queue_name="parsing-queue")
def upsert_worker(rulings: list[Ruling]):
    """
    Takes fetched rulings and upserts them into DBs.
    """
    ruling_ids = [ruling.ruling_id for ruling in rulings]
    try:
        logger.info(f"Upserting ({len(ruling_ids)}) rulings:", ruling_ids=ruling_ids)

        embedding_db.upsert_rulings(rulings)
        document_db.upsert_rulings(rulings)

        logger.info(
            f"Upserted ({len(ruling_ids)}) rulings into DB:", ruling_ids=ruling_ids
        )
    except Exception:
        logger.exception(
            "Error while parsing rulings into DB:",
            ruling_ids=ruling_ids if ruling_ids else "N/A",
        )
        raise Exception


def construct_fetch_upsert_pipeline(*args, **kwargs):
    return dramatiq.pipeline(
        [
            fetch_worker.message(*args, **kwargs),
            upsert_worker.message(),
        ]
    )
