import re


MAX_QUERY_LENGTH = 20_000


FORBIDDEN_SQL = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "ATTACH",
    "DETACH",
    "COPY",
    "INSTALL",
    "LOAD",
    "CALL",
    "PRAGMA",
}

# DuckDB table functions can read arbitrary local files or invoke external
# extensions even when the outer statement is a SELECT. The analysis engine
# registers only the in-memory `dataset` relation, so these sources are never
# needed for a valid user analysis.
FORBIDDEN_TABLE_FUNCTIONS = {
    "READ_CSV",
    "READ_CSV_AUTO",
    "READ_PARQUET",
    "CSV_SCAN",
    "PARQUET_SCAN",
    "GLOB",
    "SQLITE_SCAN",
    "POSTGRES_SCAN",
}


def validate_query(query: str) -> None:
    if not isinstance(query, str):
        raise ValueError("Query must be a string.")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError("Query exceeds the maximum permitted length.")

    # A semicolon can introduce a second statement. Queries are deliberately
    # restricted to one statement so an LLM cannot chain side effects.
    if ";" in query.rstrip().rstrip(";") or "--" in query or "/*" in query:
        raise ValueError("SQL comments and multiple statements are not allowed.")

    normalized = re.sub(
        r"\s+",
        " ",
        query.strip().upper(),
    )

    if not normalized:
        raise ValueError("Query cannot be empty.")

    for keyword in FORBIDDEN_SQL:
        if re.search(rf"\b{keyword}\b", normalized):
            raise ValueError(
                f"SQL operation '{keyword}' is not allowed."
            )

    for function in FORBIDDEN_TABLE_FUNCTIONS:
        if re.search(rf"\b{function}\s*\(", normalized):
            raise ValueError(f"SQL function '{function}' is not allowed.")

    if not normalized.startswith(("SELECT", "WITH")):
        raise ValueError(
            "Only read-only SELECT queries are allowed."
        )
