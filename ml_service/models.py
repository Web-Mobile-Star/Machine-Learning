from __future__ import annotations
import json
import os

from typing import Dict, Type
from mlflow.tracking.client import MlflowClient

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime

from ml_service.database import Base
from ml_service.helper import (
    SingletonMeta,
    engine_from_env,
    table_name_to_class_name,
)


TABLE_PREFIX = "some_unique_prefix_"
UUID_KEY = "uuid"
TIMESTAMP_KEY = "prediction_timestamp"
INPUT_TABLE_NAME = "inputs"
OUTPUT_TABLE_NAME = "outputs"
PREFIXED_INPUT_TABLE_NAME = f"{TABLE_PREFIX}{INPUT_TABLE_NAME}"
PREFIXED_OUTPUT_TABLE_NAME = f"{TABLE_PREFIX}{OUTPUT_TABLE_NAME}"
_UUID_TYPE = Column(String, primary_key=True, index=True)


def sql_alchemy_column_from_name_and_type(
    column_name: str, data_type: str
) -> Table:
    if "int" in data_type:
        sql_type = Integer
    elif "float" in data_type:
        sql_type = Float
    elif data_type == "str" or data_type == "object":
        sql_type = String
    else:
        raise ValueError(f"Don't know what type to use for {data_type}")

    return Column(column_name, sql_type)


def sql_alchemy_columns_from_schema(
    schema: Dict[str, str]
) -> Dict[str, Column]:
    sql_alchemy_types: Dict[str, Column] = {}
    for column_name, column_type in schema.items():
        sql_alchemy_types[column_name] = sql_alchemy_column_from_name_and_type(
            column_name, column_type
        )
    return sql_alchemy_types


def input_table_from_schema(schema: Dict[str, str]) -> Table:
    sql_alchemy_types = sql_alchemy_columns_from_schema(schema)
    sql_alchemy_types[TIMESTAMP_KEY] = Column(TIMESTAMP_KEY, DateTime)
    sql_alchemy_types[UUID_KEY] = Column(
        UUID_KEY, String, primary_key=True, index=True
    )
    prefixed_output_table_name = f"{TABLE_PREFIX}{OUTPUT_TABLE_NAME}"
    sql_alchemy_types[OUTPUT_TABLE_NAME] = relationship(
        table_name_to_class_name(prefixed_output_table_name),
        back_populates=INPUT_TABLE_NAME,
        uselist=False,
    )
    return create_model_class(PREFIXED_INPUT_TABLE_NAME, sql_alchemy_types)


def output_table_from_schema(schema: Dict[str, str]) -> Table:
    sql_alchemy_types = sql_alchemy_columns_from_schema(schema)
    prefixed_output_table_name = f"{TABLE_PREFIX}{INPUT_TABLE_NAME}"
    sql_alchemy_types[INPUT_TABLE_NAME] = relationship(
        table_name_to_class_name(prefixed_output_table_name),
        back_populates=OUTPUT_TABLE_NAME,
        uselist=False,
    )
    sql_alchemy_types[UUID_KEY] = Column(
        UUID_KEY,
        String,
        ForeignKey(f"{PREFIXED_INPUT_TABLE_NAME}.{UUID_KEY}"),
    )
    sql_alchemy_types["id"] = Column("id", Integer, primary_key=True)
    return create_model_class(PREFIXED_OUTPUT_TABLE_NAME, sql_alchemy_types)


def create_model_class(table_name: str, sql_alchemy_types: Dict) -> Type:
    class_name = table_name_to_class_name(table_name)
    clas = type(
        class_name,
        (Base,),
        {
            # data members
            "__tablename__": table_name,
            **sql_alchemy_types,
        },
    )
    return clas


class ModelMakerSingleton(metaclass=SingletonMeta):
    def __init__(
        self,
        run_id: str = None,
    ):
        assert run_id is not None

        input_schema_path = "input_schema.json"
        output_schema_path = "output_schema.json"
        mlflow_client = MlflowClient()
        input_schema_path_local = mlflow_client.download_artifacts(
            os.environ["RUN_ID"], input_schema_path
        )
        output_schema_path_local = mlflow_client.download_artifacts(
            os.environ["RUN_ID"], output_schema_path
        )
        with open(input_schema_path_local, "r") as f:
            input_schema_dict = json.load(f)
        with open(output_schema_path_local, "r") as f:
            output_schema_dict = json.load(f)
        input_table = input_table_from_schema(input_schema_dict)
        output_table = output_table_from_schema(output_schema_dict)
        engine = engine_from_env()
        input_table.metadata.create_all(bind=engine)
        output_table.metadata.create_all(bind=engine)
        self.input_table = input_table
        self.output_table = output_table
