import json

import pytest
from fastapi.testclient import TestClient

from robojudge.main import app
from robojudge.db.mongo_db import document_db
from robojudge.utils.internal_types import Ruling


client = TestClient(app)


@pytest.fixture(scope="session")
def rulings_in_mongo():
    with open("tests/assets/rulings_in_mongo.json", "r") as rf:
        rulings_json = json.load(rf)
        return [Ruling(**json_ruling) for json_ruling in rulings_json]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"


def test_get_all_rulings(rulings_in_mongo: list[Ruling]):
    document_db.upsert_rulings(rulings_in_mongo)

    response = client.get("/rulings")

    rulings_from_response = response.json()

    assert response.status_code == 200
    assert len(rulings_from_response) == 3
    assert set(
        [response_ruling["ruling_id"] for response_ruling in rulings_from_response]
    ) == set([ruling.ruling_id for ruling in rulings_in_mongo])
