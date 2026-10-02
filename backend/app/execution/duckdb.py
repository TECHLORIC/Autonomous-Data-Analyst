from pathlib import Path

import duckdb
import pandas as pd

from app.execution.query import validate_query


DEFAULT_RESULT_LIMIT = 1_000

class DuckDBEngine:
    """Analytical engine for executing SQL against datasets."""

    def __init__(self) -> None:
        self.connection = duckdb.connect(database=":memory:")
        # Security Hardening: Prevent LLM-injected SQL from reading/writing host files
        self.connection.execute("SET enable_external_access=false;")

    def load_dataframe(
        self,
        dataframe: pd.DataFrame,
        table_name: str = "dataset",
    ) -> None:
        self.connection.register(table_name, dataframe)

    def execute(
        self,
        query: str,
        result_limit: int = DEFAULT_RESULT_LIMIT,
    ) -> list[dict]:
        validate_query(query)

        if result_limit <= 0:
            raise ValueError("Result limit must be positive.")

        # Apply the cap inside DuckDB rather than fetching a potentially
        # unbounded result set into application memory.
        bounded_query = (
            f"SELECT * FROM ({query.rstrip().rstrip(';')}) "
            f"AS analysis_result LIMIT {int(result_limit)}"
        )
        result = self.connection.execute(bounded_query)

        columns = [
            description[0]
            for description in result.description
        ]

        return [
            dict(zip(columns, row))
            for row in result.fetchall()
        ]

    def load_file(
        self,
        file_path: Path,
        table_name: str = "dataset",
    ) -> None:
        extension = file_path.suffix.lower()

        if extension == ".csv":
            query = f"""
                CREATE OR REPLACE TABLE {table_name}
                AS SELECT *
                FROM read_csv_auto('{file_path.as_posix()}')
            """

        elif extension == ".parquet":
            query = f"""
                CREATE OR REPLACE TABLE {table_name}
                AS SELECT *
                FROM read_parquet('{file_path.as_posix()}')
            """

        else:
            raise ValueError(
                f"DuckDB file loading does not support {extension}"
            )

        self.connection.execute(query)

    def close(self) -> None:
        self.connection.close()
