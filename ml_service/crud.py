from datetime import datetime
from ml_service.models import TIMESTAMP_KEY, UUID_KEY
from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table


def store_request_and_result(
    db: Session,
    request_uuid: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    input_table_model: Table,
    output_table_model: Table,
) -> str:
    timestamp = datetime.now()
    request_data[UUID_KEY] = request_uuid
    request_data[TIMESTAMP_KEY] = timestamp
    input_db_entry = input_table_model(**request_data)
    db.add(input_db_entry)
    output_db_entry = output_table_model(**response_data)
    db.add(output_db_entry)
    db.commit()
    db.refresh(input_db_entry)
    return input_db_entry.uuid


def get_request_and_result(
    db: Session, request_uuid: str, input_table_model: Table
):
    return (
        db.query(input_table_model)
        .filter(input_table_model.uuid == request_uuid)
        .first()
    )
