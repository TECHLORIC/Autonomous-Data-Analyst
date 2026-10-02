import pytest

from app.execution.query import validate_query


def test_rejects_delete() -> None:
    with pytest.raises(ValueError):
        validate_query(
            "DELETE FROM dataset"
        )


def test_rejects_drop() -> None:
    with pytest.raises(ValueError):
        validate_query(
            "DROP TABLE dataset"
        )


def test_accepts_select() -> None:
    validate_query(
        "SELECT * FROM dataset"
    )