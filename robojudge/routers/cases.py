import asyncio
from threading import Thread

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import PlainTextResponse

from robojudge.tasks.case_scraping import run_scraping_instance
from robojudge.utils.logger import logging
from robojudge.utils.api_types import (
    CaseQuestionRequest,
    CaseSearchRequest,
    CaseQuestionResponse,
)
from robojudge.utils.internal_types import CaseWithSummary
from robojudge.db.chroma_db import embedding_db
from robojudge.db.mongo_db import document_db
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer
from robojudge.components.summarizer.langchain_summarizer import summarizer
from robojudge.components.summarizer.case_title_generator import title_generator

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/cases", tags=["Cases"])


async def prepare_summary_and_title(case: CaseWithSummary):
    if not case.summary:
        case.summary = await summarizer.summarize(case.reasoning)
    if not case.title:
        case.title = await title_generator.generate_title(case.summary)


@router.get("/")
async def get_all_cases():
    return embedding_db.get_all_cases()


@router.put("/search", response_model=list[CaseWithSummary])
async def search_cases(request: CaseSearchRequest, bg_tasks: BackgroundTasks):
    """
    Given a string, searches for the most similar texts in a vector DB of court cases.
    If a part of the case is similar, it is returned alongside a summary of the whole case (if requested).
    """
    logger.info(f'Searching for similar text chunks:"{request.query_text}".')

    # Find the most similar text chunks of saved cases
    case_chunks = embedding_db.find_case_chunks_by_text(
        query_text=request.query_text, limit=request.max_results
    )
    case_ids = set(case.case_id for case in case_chunks)

    cases_with_summary = []

    # Find the whole cases in document DB
    cases_in_document_db = list(
        document_db.collection.find({"case_id": {"$in": list(case_ids)}})
    )
    for case_in_doc_db in cases_in_document_db:
        cases_with_summary.append(
            CaseWithSummary(**case_in_doc_db, id=case_in_doc_db["case_id"])
        )

    if request.generate_summaries:
        await asyncio.gather(*map(prepare_summary_and_title, cases_with_summary))
        # Cache the results if the cases are retrieved in the future
        bg_tasks.add_task(document_db.add_document_summaries, cases_with_summary)
        # Thread(
        #     target=lambda: document_db.add_document_summaries(cases_with_summary)
        # ).start()

    return cases_with_summary


@router.put("/{case_id}/question", response_model=CaseQuestionResponse)
async def answer_case_question(case_id: str, request: CaseQuestionRequest):
    """
    Given a `case_id` and a question, an LLM tries to answer that question by searching through the text (reasoning) of the case.
    """
    logger.info(f'Answering question about case "{case_id}": "{request.question}".')

    case = document_db.collection.find_one({"case_id": case_id})

    answer = await CaseQuestionAnswerer.answer_question(
        request.question, case["reasoning"]
    )

    return CaseQuestionResponse(answer=answer)


@router.put("/scrape")
async def fetch_cases(bg_tasks: BackgroundTasks):
    """
    Manually triggers one instance/batch of scraping cases from the justice ministry's website.
    """
    logger.info("Triggering case scraping based on an API request.")
    bg_tasks.add_task(run_scraping_instance)
    # Thread(target=lambda: asyncio.run(fetch_new_cases())).start()
    return PlainTextResponse("ok", 202)
