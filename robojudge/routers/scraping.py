from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
    Path,
    HTTPException,
)
from fastapi.responses import PlainTextResponse
from fastapi_limiter.depends import RateLimiter

from robojudge.utils.api_types import (
    FetchCasesRequest,
    FetchCasesResponse,
    FetchCasesStatusResponse,
)
from robojudge.utils.logger import logger
from robojudge.utils.settings import settings
from robojudge.tasks.case_scraping import (
    scraper_parser_pipeline,
    construct_filtered_ruling_pipeline,
)
from robojudge.utils.functional import generate_uuid
from robojudge.db.mongo_db import document_db, DocumentStorage


router = APIRouter(prefix="/scraping")


@router.post(
    "/run",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    include_in_schema=False,
)
async def fetch_cases(request: Request):
    """
    Manually triggers one instance/batch of scraping cases from the justice ministry's website.
    Debugging endpoint, disabled for production.
    """
    if settings.ENVIRONMENT != "dev":
        raise HTTPException(400, "Invalid for production use.")
    logger.info("Triggering case scraping based on an API request.")
    scraper_parser_pipeline.run()
    return PlainTextResponse("ok", 202)


@router.post(
    "/schedule",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    tags=["scraping"],
    status_code=202,
    response_model=FetchCasesResponse,
)
async def fetch_specified_cases(
    request: FetchCasesRequest,
):
    """
    Schedules an asynchronous job to scrape rulings based on the provided filters and limit.
    """
    fetch_job_token = generate_uuid()
    payload = {"token": fetch_job_token}

    construct_filtered_ruling_pipeline(fetch_job_token, request).run()

    return payload


@router.get(
    "/{fetch_job_token}",
    response_model=FetchCasesStatusResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
    tags=["scraping"],
)
async def get_cases_by_fetch_job_token(
    request: Request,
    fetch_job_token: Annotated[str, Path()],
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    """
    Returns the status and associated rulings based on the provided `fetch_job_token`.
    """
    fetch_job = document_db.scraping_job_collection.find_one({"token": fetch_job_token})

    if not fetch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Fetch job with token "{fetch_job_token}" was not found.',
        )

    cases = document_db.collection.find(
        {"case_id": {"$in": fetch_job["scraped_ruling_ids"]}}
    )
    response = FetchCasesStatusResponse(status=fetch_job["status"], content=list(cases))

    return response
