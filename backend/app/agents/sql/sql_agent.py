import json
from typing import Any

from app.data.access import DatasetAccess
from app.execution.duckdb import DuckDBEngine
from app.services.llm import LLMService


class SQLAgent:

    SYSTEM_PROMPT = """
You are an SQL analysis agent for DuckDB.

Your job is to convert an analysis task into
a single SQL SELECT query.

Rules:

1. Return ONLY valid JSON.

2. Only generate SELECT queries.

3. Never use:
   - INSERT
   - UPDATE
   - DELETE
   - DROP
   - ALTER
   - CREATE
   - TRUNCATE
   - ATTACH
   - DETACH
   - COPY

4. Use the table name provided.

5. Do not invent columns.

6. Use only columns available in the dataset profile.

7. IMPORTANT DATE HANDLING:
   Dataset date columns may be stored as VARCHAR strings.
   NEVER assume that:
       CAST(date_column AS DATE)
   will work.

8. If a date column contains values in DD-MM-YYYY format,
   parse it using:
       strptime("date_column", '%d-%m-%Y')

9. For monthly grouping of a DD-MM-YYYY date column, use:
       strftime(strptime("date_column", '%d-%m-%Y'), '%Y-%m')

10. For YYYY-MM-DD date strings, CAST(... AS DATE) may be used.

11. Use the actual date format identified from the
    dataset profile whenever available.

12. Use valid DuckDB SQL syntax.

13. Do not perform calculations yourself.
    Generate SQL that DuckDB can execute.

14. ALWAYS use aggregation (SUM, AVG, COUNT, MIN, MAX) and GROUP BY when calculating totals, breakdowns, or performance metrics.

15. Limit output to at most 20 rows using ORDER BY ... DESC LIMIT 20 for grouping tasks to prevent massive result sets.

16. NEVER return raw "SELECT *" dumps when calculating analytics. Always select relevant columns and aggregates.

Required format:

{
    "query": "SELECT ...",
    "explanation": "short explanation"
}
"""

    def __init__(
        self,
        llm: LLMService,
    ) -> None:

        self.llm = llm

        self.dataset_access = DatasetAccess()

    async def generate_query(
        self,
        task: str,
        dataset_profile: dict[str, Any],
        table_name: str = "dataset",
    ) -> dict[str, str]:

        prompt = f"""
Dataset table:

{table_name}

Dataset profile:

{json.dumps(dataset_profile, default=str)}

Analysis task:

{task}

Generate the SQL query.
"""

        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        try:

            result = json.loads(response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "SQL agent returned invalid JSON."
            ) from exc

        if "query" not in result:

            raise ValueError(
                "SQL agent response does not contain a query."
            )

        return result

    async def execute(
        self,
        task: str,
        dataset_profile: dict[str, Any],
        dataset_id: str,
        **kwargs,
    ) -> dict[str, Any]:

        generated = await self.generate_query(
            task=task,
            dataset_profile=dataset_profile,
        )

        query = generated["query"]

        dataframe = (
            self.dataset_access.load_dataframe(
                dataset_id,
                file_path=kwargs.get("file_path", "")
            )
        )

        engine = DuckDBEngine()

        try:

            engine.load_dataframe(
                dataframe,
                "dataset",
            )

            results = engine.execute(query)

            return {
                "task": task,
                "tool": "sql",
                "query": query,
                "explanation": generated.get(
                    "explanation",
                    "",
                ),
                "results": results,
            }

        finally:

            engine.close()
