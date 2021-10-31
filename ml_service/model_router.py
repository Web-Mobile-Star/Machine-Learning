from mlflow.tracking.client import MlflowClient
from sqlalchemy.engine import create_engine
from ml_service.helper import SingletonMeta, postgres_connection_from_env
from ml_service.crud import store_request_and_result
import uuid
from ml_service.database import SessionMakerSingleton
from ml_service.models import ModelMakerSingleton
import os
from typing import Optional

import pandas as pd
from pandas._testing import assert_frame_equal
import mlflow
import mlflow.sklearn
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sklearn.pipeline import Pipeline

router = APIRouter()


class RequestItem(BaseModel):
    PassengerId: int
    Pclass: int
    Name: str
    Sex: str
    Age: int
    SibSp: int
    Parch: int
    Fare: float
    Cabin: str
    Ticket: Optional[str]
    Embarked: str


class ResponseItem(BaseModel):
    uuid: str
    probability_of_death: float


def _load_model() -> Pipeline:
    run_id = os.environ["RUN_ID"]
    model_uri = f"runs:/{run_id}/model"
    # Load your model using mlflow.sklearn.load_model

    # Download the example inputs and outputs and ensure that the model
    # is behaving as expected

    # return the pipeline


def _load_db_models() -> ModelMakerSingleton:
    return ModelMakerSingleton(os.environ["RUN_ID"])


def _load_db():
    model_maker = _load_db_models()
    postgres_connection_string = postgres_connection_from_env()
    engine = create_engine(postgres_connection_string)
    return SessionMakerSingleton(
        engine,
        model_maker.input_table,
        model_maker.output_table,
    ).sessionmaker()


@router.post("/predict")
async def predict(
    request_item: RequestItem,
    background_tasks: BackgroundTasks,
    ml_model: Pipeline = Depends(_load_model),
    db=Depends(_load_db),
    db_models=Depends(_load_db_models),
):
    df = pd.json_normalize(request_item.dict())
    probability = ml_model.predict_proba(df)[0, 0]
    request_uuid = str(uuid.uuid4())
    response_data = {
        "probability_of_death": probability,
        "uuid": request_uuid,
    }
    background_tasks.add_task(
        store_request_and_result,
        db,
        request_uuid,
        request_item.dict(),
        response_data,
        db_models.input_table,
        db_models.output_table,
    )
    return response_data
