import pytest

from ml_service.helper import table_name_to_class_name


@pytest.mark.parametrize(
    "table_name, expected_class_name", [("abcd_1", "Abcd1")]
)
def test_table_name_to_class_name(table_name: str, expected_class_name: str):
    assert table_name_to_class_name(table_name) == expected_class_name
