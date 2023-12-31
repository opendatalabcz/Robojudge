import asyncio
from typing import Annotated, Optional

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

from robojudge.tasks.case_scraping import run_scraping_instance
from robojudge.utils.logger import logging
from robojudge.utils.api_types import (
    CaseQuestionRequest,
    CaseSearchRequest,
    CaseQuestionResponse,
    FetchCasesRequest,
    FetchCasesStatusResponse,
)
from robojudge.utils.internal_types import Case, CaseChunk, CaseFetchJob
from robojudge.tasks.scraper_pool import pool
from robojudge.components.paginating_scraper import PaginatingScraper
from robojudge.utils.settings import settings
from robojudge.utils.functional import generate_uuid, construct_server_url
from robojudge.db.chroma_db import embedding_db, CaseEmbeddingStorage
from robojudge.db.mongo_db import document_db, DocumentStorage
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer
from robojudge.components.summarizer.langchain_summarizer import summarizer
from robojudge.components.summarizer.case_title_generator import title_generator

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


async def prepare_summary_and_title(case: Case):
    if not case.summary:
        case.summary = await summarizer.summarize(case.reasoning)
    if not case.title:
        case.title = await title_generator.generate_title(case.summary)


@router.get("/chunks", response_model=list[CaseChunk])
async def get_all_case_chunks(
    embedding_db: Annotated[CaseEmbeddingStorage, Depends(embedding_db)]
):
    return embedding_db.get_all_cases()


@router.get("", response_model=list[Case])
async def get_all_cases(
    document_db: Annotated[DocumentStorage, Depends(document_db)],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
):
    db_documents = document_db.collection.find({}).skip(offset).limit(limit)
    response_documents: list[Case] = []
    for db_doc in db_documents:
        response_documents.append(Case(**db_doc))

    return response_documents


# TODO: docs for request filter params
# TODO: notify about errored case_ids (save info into DB)
@router.post("/fetch")
async def fetch_specified_cases(
    request: FetchCasesRequest,
):
    fetch_job_token = generate_uuid()
    payload = {"token": fetch_job_token}

    pool.queue.put({"token": fetch_job_token, "request": request})

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=payload)


# TODO: add token expiration?
@router.get("/fetch/{fetch_job_token}", response_model=FetchCasesStatusResponse)
async def get_cases_by_fetch_job_token(
    fetch_job_token: Annotated[str, Path()],
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    fetch_job = document_db.fetch_job_collection.find_one({"token": fetch_job_token})

    if not fetch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Fetch job with token "{fetch_job_token}" was not found.',
        )

    cases = document_db.collection.find({"case_id": {"$in": fetch_job["case_ids"]}})
    response = FetchCasesStatusResponse(status=fetch_job["status"], content=list(cases))

    return response


@router.post("/search", response_model=list[Case])
async def search_cases(
    request: CaseSearchRequest,
    bg_tasks: BackgroundTasks,
    embedding_db: Annotated[CaseEmbeddingStorage, Depends(embedding_db)],
    document_db: Annotated[DocumentStorage, Depends(document_db)],
):
    """
    Given a string, searches for the most similar texts in a vector DB of court cases.
    If a part of the case is similar, it is returned alongside a summary of the whole case (if requested).
    """
    logger.info(f'Searching for similar text chunks:"{request.query_text}".')

    # Find the most similar text chunks of saved cases
    case_chunks = embedding_db.find_case_chunks_by_text(
        query_text=request.query_text, limit=request.limit
    )
    case_ids = set(case.case_id for case in case_chunks)

    cases_with_summary: list[Case] = []

    # Find the whole cases in document DB
    cases_in_document_db = list(
        document_db.collection.find({"case_id": {"$in": list(case_ids)}})
    )
    for case_in_doc_db in cases_in_document_db:
        cases_with_summary.append(Case(**case_in_doc_db))

    if request.generate_summaries:
        await asyncio.gather(*map(prepare_summary_and_title, cases_with_summary))
        # Cache the results if the cases are retrieved in the future
        bg_tasks.add_task(document_db.add_document_summaries, cases_with_summary)

    return cases_with_summary


@router.post("/{case_id}/question", response_model=CaseQuestionResponse)
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


@router.post("/scrape")
async def fetch_cases(bg_tasks: BackgroundTasks):
    """
    Manually triggers one instance/batch of scraping cases from the justice ministry's website.
    """
    logger.info("Triggering case scraping based on an API request.")
    bg_tasks.add_task(run_scraping_instance)
    return PlainTextResponse("ok", 202)
