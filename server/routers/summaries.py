from threading import Thread
import asyncio

from fastapi import APIRouter

from server.db.mongo_db import document_db
from server.db.chroma_db import embedding_db
from server.routers.cases import CaseSearchRequest
from server.utils.types import CaseWithSummary
from server.components.summarizer.gpt_summarizer import GPTSummarizer

router = APIRouter(prefix='/summary')


def upload_summaries_to_db(case_summaries: list[CaseWithSummary]):
    document_db.add_document_summaries(case_summaries)

async def prepare_summary(case: CaseWithSummary):
    if not case.summary:
        # Find all chunks for the case_ids and put them together to create the original whole reasoning
        case_chunks = embedding_db.collection.get(ids=[], where={"case_id": {
            "$eq": case.id
        }})

        text = '\n'.join(case_chunks['documents'])
        case.summary = await GPTSummarizer(text, case.id).summarize_text()

@router.post('/search', response_model=list[CaseWithSummary])
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())
    case_ids = set(case.case_id for case in cases)

    cases_in_document_db = list(document_db.collection.find(
        {"case_id": {"$in": list(case_ids)}}))
    case_map = {summary['case_id']: {**summary, "id": summary['case_id']}
                for summary in cases_in_document_db}

    cases_with_summary = []
    for case_id in case_ids:
        case_with_summary = CaseWithSummary(**case_map.get(case_id, ''))
        cases_with_summary.append(case_with_summary)

    await asyncio.gather(*map(prepare_summary, cases_with_summary))

    Thread(target=upload_summaries_to_db, args=(cases_with_summary,)).start()

    return cases_with_summary
