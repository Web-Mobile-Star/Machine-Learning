import time

from sqlalchemy.sql.schema import Table
from ml_service.crud import get_request_and_result
from ml_service.database import SessionMakerSingleton
from typing import Dict

import pytest
from fastapi.testclient import TestClient


def test_predict_endpoint_without_body_fails(test_client: TestClient):
    response = test_client.post("/predict")
    assert response.status_code == 422


def test_predict_endpoint_can_validate_request(
    test_client: TestClient, example_request: Dict
):
    response = test_client.post("/predict", json=example_request)
    assert response.status_code == 200


def test_predict_endpoint_returns_prediction(
    test_client: TestClient, example_request: Dict
):
    response = test_client.post("/predict", json=example_request)
    assert response.json()["probability_of_death"] == 0.9


def test_predict_endpoint_stored_to_db(
    test_client: TestClient,
    example_request: Dict,
    session_maker_singleton: SessionMakerSingleton,
    input_table_model: Table,
):
    response = test_client.post("/predict", json=example_request)
    time.sleep(1)
    print(f"response: {response.json()}")
    queryed_entry = get_request_and_result(
        session_maker_singleton.sessionmaker(),
        response.json()["uuid"],
        input_table_model,
    )
    for k, v in example_request.items():
        assert getattr(queryed_entry, k) == v
    assert getattr(queryed_entry.outputs, "probability_of_death") == 0.9


@pytest.fixture
def example_request() -> Dict:
    return {
        "passenger_id": 1,
        "pclass": 3,
        "name": "Braund, Mr. Owen Harris",
        "sex": "male",
        "age": 22,
        "sib_sp": 1,
        "parch": 0,
        "ticket": "A/5 21171",
        "fare": 7.25,
        "cabin": "",
        "embarked": "S",
    }
