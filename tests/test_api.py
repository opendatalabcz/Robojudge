import datetime
import json

import pytest
from fastapi.testclient import TestClient

from robojudge.main import app
from robojudge.db.mongo_db import document_db
from robojudge.utils.internal_types import Case, ScrapingJob, ScrapingFilters


client = TestClient(app)


@pytest.fixture(scope="session")
def cases_in_mongo():
    with open("tests/assets/cases_in_mongo.json", "r") as rf:
        cases_json = json.load(rf)
        return [Case(**json_case) for json_case in cases_json]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"


def test_get_all_cases(cases_in_mongo: list[Case]):
    document_db.upsert_documents(cases_in_mongo)

    response = client.get("/cases")

    cases_from_response = response.json()

    assert response.status_code == 200
    assert len(cases_from_response) == 2
    assert set(
        [response_case["case_id"] for response_case in cases_from_response]
    ) == set([case.case_id for case in cases_in_mongo])


def test_trigger_fetch():
    filters = ScrapingFilters(
        judge_firstname="Petr",
        judge_lastname="Blažej",
        publication_date_from="2023-05-12",
        publication_date_to="2023-05-19",
    )

    trigger_response = client.post("/scraping/schedule", json={"filters": filters.dict()})
    fetch_job_response = trigger_response.json()

    assert trigger_response.status_code == 202
    assert fetch_job_response["token"]


def test_get_cases_by_fetch_job_token(cases_in_mongo: list[Case]):
    case_ids = [case.case_id for case in cases_in_mongo]
    token = "very-special-token"
    fetch_job = ScrapingJob(
        token=token,
        scraped_ruling_ids=case_ids,
        started_at=datetime.datetime.now()
    )

    document_db.upsert_documents(cases_in_mongo)
    document_db.scraping_job_collection.insert_one(fetch_job.dict())

    response = client.get(f"/scraping/{token}")

    fetch_job_response = response.json()

    assert response.status_code == 200
    assert len(fetch_job_response["content"]) == 2
    assert set(
        [response_case["case_id"] for response_case in fetch_job_response["content"]]
    ) == set(case_ids)
