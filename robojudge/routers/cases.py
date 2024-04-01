import asyncio
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    status,
    Request,
    HTTPException,
)
from fastapi_limiter.depends import RateLimiter

from robojudge.components.reasoning.query_checker import query_checker
from robojudge.components.summarizer.prepare_summary import prepare_summary_and_title
from robojudge.utils.api_types import (
    CaseQuestionRequest,
    CaseSearchRequest,
    CaseQuestionResponse,
    SearchCasesResponse,
)
from robojudge.utils.settings import settings
from robojudge.utils.logger import logger
from robojudge.utils.internal_types import Case, CaseChunk
from robojudge.db.chroma_db import embedding_db, CaseEmbeddingStorage
from robojudge.db.mongo_db import document_db, DocumentStorage
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer


router = APIRouter(prefix="/cases")


@router.get(
    "",
    response_model=list[Case],
    dependencies=[Depends(RateLimiter(times=30, seconds=60))]
    if settings.ENVIRONMENT == "prod"
    else [],
    tags=["rulings"],
)
async def get_all_cases(
    request: Request,
    document_db: Annotated[DocumentStorage, Depends(document_db)],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query(le=100, description="Page size")] = 100,
):
    """
    Paginates over all cases.
    """
    db_documents = document_db.collection.find({}).skip(offset).limit(limit)
    response_documents: list[Case] = []
    for db_doc in db_documents:
        response_documents.append(Case(**db_doc))

    return response_documents


@router.post(
    "/search",
    response_model=SearchCasesResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
    if settings.ENVIRONMENT == "prod"
    else [],
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
        logger.info(f'Query was deemed irrelevant:"{search_request.query_text}".')
        return SearchCasesResponse(relevance=False, reasoning=relevance["reasoning"])

    logger.info(f'Searching for similar text chunks:"{search_request.query_text}".')

    # Find the most similar text chunks of saved cases
    case_chunks = embedding_db.find_rulings_by_text(
        query_text=search_request.query_text,
        offset=search_request.current_page * search_request.page_size,
        n_results=search_request.page_size,
        filters=search_request.filters,
    )
    case_ids = [str(case.metadata.case_id) for case in case_chunks]
    logger.info(f'Vector DB returned similar ruling_ids: "{case_ids}".')

    cases_with_summary: list[Case] = []
    # Find the whole cases in document DB
    for case_id in case_ids:
        case_in_doc_db = document_db.collection.find_one({"case_id": case_id})
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
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
    if settings.ENVIRONMENT == "prod"
    else [],
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
    """
    Debugging endpoint, disabled for production.
    """
    if settings.ENVIRONMENT != "dev":
        raise HTTPException(400, "Invalid for production use.")
    return embedding_db.get_all_case_chunks()
