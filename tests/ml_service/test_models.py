from datetime import datetime
from typing import Any, Dict

from sqlalchemy.sql.schema import Table

from ml_service.models import (
    PREFIXED_INPUT_TABLE_NAME,
    PREFIXED_OUTPUT_TABLE_NAME,
    TIMESTAMP_KEY,
    UUID_KEY,
)


def test_can_create_input_table(db_engine_with_tables):
    table_exists = db_engine_with_tables.dialect.has_table(
        db_engine_with_tables, PREFIXED_INPUT_TABLE_NAME
    )
    assert table_exists


def test_can_create_output_table(db_engine_with_tables):

    table_exists = db_engine_with_tables.dialect.has_table(
        db_engine_with_tables, PREFIXED_OUTPUT_TABLE_NAME
    )
    assert table_exists


def test_can_instantiate_input_model(
    input_table_model: Table, input_data_example: Dict[str, Any]
):
    input_data_example[UUID_KEY] = "abcd"
    input_data_example[TIMESTAMP_KEY] = datetime.now()
    input_table_model(**input_data_example)


def test_can_instantiate_output_model(
    output_table_model: Table, output_data_example: Dict[str, str]
):
    output_table_model(**output_data_example)
