import asyncio
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    status,
    Request,
    Path,
    HTTPException,
)
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi_limiter.depends import RateLimiter

from robojudge.components.reasoning.query_checker import query_checker
from robojudge.utils.logger import logging
from robojudge.utils.api_types import (
    CaseQuestionRequest,
    CaseSearchRequest,
    CaseQuestionResponse,
    FetchCasesRequest,
    FetchCasesStatusResponse,
    SearchCasesResponse,
)
from robojudge.utils.internal_types import Case, CaseChunk
from robojudge.utils.settings import settings, SUMMARY_UNAVAILABLE_MESSAGE
from robojudge.utils.internal_types import Case, CaseChunk
from robojudge.tasks.case_scraping import (
    run_scraper_parser_pipeline,
    run_filtered_scraper_parser_pipeline,
)
from robojudge.utils.settings import settings
from robojudge.utils.functional import generate_uuid
from robojudge.db.chroma_db import embedding_db, CaseEmbeddingStorage
from robojudge.db.mongo_db import document_db, DocumentStorage
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer
from robojudge.components.summarizer.langchain_summarizer import summarizer
from robojudge.components.summarizer.case_title_generator import title_generator

# TODO: structlog
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/cases")


# TODO: move
async def prepare_summary_and_title(case: Case):
    if not case.summary or case.summary == SUMMARY_UNAVAILABLE_MESSAGE:
        logging.info(f'Generating summary for text: "{case.reasoning[:200]}..."')
        summary = await summarizer.summarize(case.reasoning)
        case.summary = summary if summary else SUMMARY_UNAVAILABLE_MESSAGE
    if not case.title and case.summary != SUMMARY_UNAVAILABLE_MESSAGE:
        case.title = await title_generator.generate_title(case.summary)


@router.get(
    "/chunks",
    response_model=list[CaseChunk],
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
    include_in_schema=False,
)
async def get_all_case_chunks(
    request: Request,
    embedding_db: Annotated[CaseEmbeddingStorage, Depends(embedding_db)],
):
    if settings.ENVIRONMENT != "dev":
        raise HTTPException(400, "Invalid for production use.")
    return embedding_db.get_all_cases()


# TODO: document (summary/description, example?)


@router.get(
    "",
    response_model=list[Case],
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
    tags=["rulings"],
    description="Paginate over all cases.",
)
async def get_all_cases(
    request: Request,
    document_db: Annotated[DocumentStorage, Depends(document_db)],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100, description="Page size")] = 100,
):
    db_documents = document_db.collection.find({}).skip(offset).limit(limit)
    response_documents: list[Case] = []
    for db_doc in db_documents:
        response_documents.append(Case(**db_doc))

    return response_documents


# TODO: docs for request filter params
# TODO: notify about errored case_ids (save info into DB)
@router.post(
    "/fetch",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    tags=["scraping"],
)
async def fetch_specified_cases(
    request: FetchCasesRequest,
):
    fetch_job_token = generate_uuid()
    payload = {"token": fetch_job_token}

    # TODO: investigate bug
    run_filtered_scraper_parser_pipeline(fetch_job_token, request)

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=payload)


# TODO: add token expiration?
@router.get(
    "/fetch/{fetch_job_token}",
    response_model=FetchCasesStatusResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
    tags=["scraping"],
)
async def get_cases_by_fetch_job_token(
    request: Request,
    fetch_job_token: Annotated[str, Path()],
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    fetch_job = document_db.scraping_job_collection.find_one({"token": fetch_job_token})

    if not fetch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Fetch job with token "{fetch_job_token}" was not found.',
        )

    cases = document_db.collection.find({"case_id": {"$in": fetch_job["case_ids"]}})
    response = FetchCasesStatusResponse(status=fetch_job["status"], content=list(cases))

    return response


@router.post(
    "/search",
    response_model=SearchCasesResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    tags=["rulings"],
)
async def search_cases(
    search_request: CaseSearchRequest,
    bg_tasks: BackgroundTasks,
    embedding_db: Annotated[CaseEmbeddingStorage, Depends(embedding_db)],
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    """
    Given a string, searches for the most similar texts in a vector DB of court cases.
    If a part of the case is similar, it is returned alongside a summary of the whole case (if requested).
    """
    if (
        search_request.page_size * search_request.current_page
        > settings.MAX_SEARCHABLE_RULING_COUNT
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Max limit of {settings.MAX_SEARCHABLE_RULING_COUNT} exceeded.",
        )

    relevance = await query_checker.assess_query_relevance(search_request.query_text)
    if not relevance["relevant"]:
        return SearchCasesResponse(relevance=False, reasoning=relevance["reasoning"])

    logger.info(f'Searching for similar text chunks:"{search_request.query_text}".')

    # Find the most similar text chunks of saved cases
    case_chunks = embedding_db.find_case_chunks_by_text(
        query_text=search_request.query_text,
        offset=search_request.current_page * search_request.page_size,
        n_results=search_request.page_size,
        filters=search_request.filters,
    )
    case_ids = set(case.case_id for case in case_chunks)

    logging.info(f'Vector DB returned similar ruling_ids: "{case_ids}".')

    cases_with_summary: list[Case] = []

    # Find the whole cases in document DB
    cases_in_document_db = list(
        document_db.collection.find({"case_id": {"$in": list(case_ids)}})
    )
    for case_in_doc_db in cases_in_document_db:
        cases_with_summary.append(Case(**case_in_doc_db))

    if search_request.generate_summaries:
        await asyncio.gather(*map(prepare_summary_and_title, cases_with_summary))
        # Cache the results if the cases are retrieved in the future
        bg_tasks.add_task(document_db.add_document_summaries, cases_with_summary)

    return SearchCasesResponse(
        cases=cases_with_summary,
        relevance=True,
        max_page=settings.MAX_SEARCHABLE_RULING_COUNT / search_request.page_size,
    )


@router.post(
    "/{case_id}/question",
    response_model=CaseQuestionResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    tags=["rulings"],
)
async def answer_case_question(
    case_id: str,
    request: CaseQuestionRequest,
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    """
    Given a `case_id` and a question, an LLM tries to answer that question by searching through the text (reasoning) of the case.
    """
    logger.info(f'Answering question about case "{case_id}": "{request.question}".')

    case = Case(**document_db.collection.find_one({"case_id": case_id}))

    answer = await CaseQuestionAnswerer.answer_question(
        request.question, case.reasoning
    )

    return CaseQuestionResponse(answer=answer)


@router.post(
    "/scrape",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    include_in_schema=False,
)
async def fetch_cases(request: Request):
    """
    Manually triggers one instance/batch of scraping cases from the justice ministry's website.
    """
    if settings.ENVIRONMENT != "dev":
        raise HTTPException(400, "Invalid for production use.")
    logger.info("Triggering case scraping based on an API request.")
    run_scraper_parser_pipeline()
    return PlainTextResponse("ok", 202)
