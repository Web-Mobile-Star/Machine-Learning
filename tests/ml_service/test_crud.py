from ml_service.models import UUID_KEY
import uuid
from ml_service.database import SessionMakerSingleton
from typing import Any, Dict

from sqlalchemy.sql.schema import Table

from ml_service.crud import get_request_and_result, store_request_and_result


def test_store_and_fetch_request_and_result(
    input_data_example: Dict[str, Any],
    output_data_example: Dict[str, Any],
    session_maker_singleton: SessionMakerSingleton,
    input_table_model: Table,
    output_table_model: Table,
):
    request_uuid = str(uuid.uuid4())
    output_data_example[UUID_KEY] = request_uuid
    db = session_maker_singleton.sessionmaker()
    stored_uuid = store_request_and_result(
        db,
        request_uuid,
        input_data_example,
        output_data_example,
        input_table_model,
        output_table_model,
    )
    queryed_entry = get_request_and_result(db, stored_uuid, input_table_model)
    assert queryed_entry.uuid == stored_uuid
    for k, v in input_data_example.items():
        assert getattr(queryed_entry, k) == v
    for k, v in output_data_example.items():
        assert getattr(queryed_entry.outputs, k) == v
