import pytest

from app.execution.duckdb import DuckDBEngine
from app.execution.query import validate_query


@pytest.mark.parametrize(
    "query",
    [
        "SELECT 1; DELETE FROM dataset",
        "SELECT 1 -- hidden statement",
        "WITH data AS (SELECT 1 AS value) SELECT * FROM data; DROP TABLE dataset",
        "SELECT * FROM read_csv_auto('/etc/passwd')",
    ],
)
def test_rejects_chained_or_commented_queries(query: str) -> None:
    with pytest.raises(ValueError):
        validate_query(query)


def test_allows_read_only_common_table_expression() -> None:
    validate_query("WITH data AS (SELECT 1 AS value) SELECT * FROM data")


def test_engine_applies_result_limit() -> None:
    engine = DuckDBEngine()
    try:
        rows = engine.execute(
            "SELECT * FROM range(10) AS t(value)", result_limit=3
        )
    finally:
        engine.close()

    assert [row["value"] for row in rows] == [0, 1, 2]
