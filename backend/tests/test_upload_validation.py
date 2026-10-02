import pytest

from app.data.ingestion.validators import validate_file


def test_rejects_path_like_filename() -> None:
    with pytest.raises(ValueError, match="path"):
        validate_file("../data.csv", 10)


def test_rejects_empty_file() -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_file("data.csv", 0)
