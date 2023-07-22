from threading import Thread

from fastapi import APIRouter, Body

from server.db.mongo_db import metadata_db
from server.db.chroma_db import embedding_db
from server.model.gpt import OpenAIPrompter
from server.routers.cases import CaseSearchRequest
from server.utils.types import CaseWithSummary

router = APIRouter(prefix='/summary')


def upload_summaries_to_db(case_summaries: list[CaseWithSummary]):
    metadata_db.add_summaries(case_summaries)


@router.post('/search', response_model=list[CaseWithSummary])
async def search_cases(request: CaseSearchRequest):
    cases = embedding_db.find_case_chunks_by_text(**request.dict())
    case_ids = set(case.case_id for case in cases)

    cases_in_document_db = list(metadata_db.collection.find(
        {"case_id": {"$in": list(case_ids)}}))
    case_map = {summary['case_id']: {**summary, "id": summary['case_id']}
                for summary in cases_in_document_db}

    case_summaries = []
    for case_id in case_ids:
        case_with_summary = CaseWithSummary(**case_map.get(case_id, ''))

        if not case_with_summary.summary:
            # Find all chunks for the case_ids and put them together to create the original whole reasoning
            case_chunks = embedding_db.collection.get(ids=[], where={"case_id": {
                "$eq": case_id
            }})
            # Use the beginning and end of the reasoning for summary
            text_excerpt = '\n'.join([*case_chunks['documents'][:2],
                                     *case_chunks['documents'][-2:]])
            case_with_summary.summary = OpenAIPrompter.summarize_case(
                text_excerpt)

        case_summaries.append(case_with_summary)

    Thread(target=upload_summaries_to_db, args=(case_summaries,)).start()

    return case_summaries
