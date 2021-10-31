import os
import time
from ml_service.helper import SingletonMeta
from ml_service.database import SessionMakerSingleton
from ml_service.models import (
    input_table_from_schema,
    output_table_from_schema,
)
from typing import Any, Dict, Generator, Optional
import docker
import pytest
from sqlalchemy.sql.schema import Table
from ml_service.model_router import _load_model, _load_db, _load_db_models
from fastapi.testclient import TestClient
from sqlalchemy.engine import create_engine

from ml_service.main import app

PREDICTION_COLUMN = "probability_of_death"


@pytest.fixture(scope="session")
def docker_network() -> Generator[Optional[str], None, None]:
    if "CI_JOB_TOKEN" not in os.environ:
        network_name = "postgres_network"
        client = docker.from_env()
        network = client.networks.create(network_name)
        yield network_name
        network.remove()
    else:
        yield None


@pytest.fixture(scope="session")
def postgres_connection_string(
    docker_network: str,
) -> Generator[Optional[str], None, None]:
    if "CI_JOB_TOKEN" not in os.environ:
        pw = "wow_is_this_secret"
        container_name = "postgres"
        client = docker.from_env()
        container = client.containers.run(
            "postgres",
            ports={5432: 5432},
            detach=True,
            environment={"POSTGRES_PASSWORD": pw},
            name=container_name,
            network=docker_network,
        )
        time.sleep(2)
        yield f"postgresql://postgres:{pw}@localhost:5432/postgres"
        print(container.logs().decode())
        container.kill()
        container.remove()
    else:
        yield None


class FakeModelMakerSingleton(metaclass=SingletonMeta):
    def __init__(self, input_table: Table, output_table: Table) -> None:
        self.input_table = input_table
        self.output_table = output_table


@pytest.fixture
def test_client(
    session_maker_singleton: SessionMakerSingleton,
    fake_model_maker_singleton: FakeModelMakerSingleton,
) -> TestClient:
    app.dependency_overrides[_load_model] = _load_model_stub
    app.dependency_overrides[
        _load_db_models
    ] = lambda: fake_model_maker_singleton
    app.dependency_overrides[
        _load_db
    ] = lambda: session_maker_singleton.sessionmaker()
    return TestClient(app)


class StubModel:
    def predict_proba(self, data: Dict) -> float:
        return 0.9


def _load_model_stub() -> StubModel:
    return StubModel()


@pytest.fixture
def input_data_example() -> Dict[str, Any]:
    return {
        "PassengerId": 1,
        "Pclass": 3,
        "Name": "Braund, Mr. Owen Harris",
        "Sex": "male",
        "Age": 22,
        "SibSp": 1,
        "Parch": 0,
        "Ticket": "A/5 21171",
        "Fare": 7.25,
        "Cabin": "",
        "Embarked": "S",
    }


@pytest.fixture
def output_data_example() -> Dict[str, Any]:
    return {PREDICTION_COLUMN: 0.9}


@pytest.fixture(scope="session")
def db_engine_with_tables(db_engine, input_table_model, output_table_model):
    input_table_model.metadata.create_all(bind=db_engine)
    output_table_model.metadata.create_all(bind=db_engine)
    return db_engine


@pytest.fixture(scope="session")
def fake_model_maker_singleton(
    input_table_model: Table, output_table_model: Table
) -> FakeModelMakerSingleton:
    return FakeModelMakerSingleton(input_table_model, output_table_model)


@pytest.fixture(scope="session")
def input_table_model(input_schema_dict: Dict[str, str]) -> Table:
    return input_table_from_schema(input_schema_dict)


@pytest.fixture(scope="session")
def output_table_model(output_schema_dict: Dict[str, str]) -> Table:
    return output_table_from_schema(output_schema_dict)


@pytest.fixture(scope="session")
def input_schema_dict() -> Dict[str, str]:
    return {
        "PassengerId": "int",
        "Pclass": "int",
        "Name": "str",
        "Sex": "str",
        "Age": "int",
        "SibSp": "int",
        "Parch": "int64",
        "Ticket": "str",
        "Fare": "float",
        "Cabin": "object",
        "Embarked": "str",
    }


@pytest.fixture(scope="session")
def output_schema_dict() -> Dict[str, str]:
    return {
        PREDICTION_COLUMN: "float",
    }


@pytest.fixture(scope="session")
def db_engine(postgres_connection_string: str):
    return create_engine(postgres_connection_string)


@pytest.fixture(scope="session")
def session_maker_singleton(
    db_engine_with_tables,
    fake_model_maker_singleton: FakeModelMakerSingleton,
):
    return SessionMakerSingleton(
        db_engine_with_tables,
        fake_model_maker_singleton.input_table,
        fake_model_maker_singleton.output_table,
    )
