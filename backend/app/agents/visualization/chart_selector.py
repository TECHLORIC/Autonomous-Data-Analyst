from typing import Any


class ChartSelector:

    def select_chart(
        self,
        results: list[dict[str, Any]],
        question: str,
    ) -> dict[str, Any]:

        if not results:

            return {
                "chart_type": "table",
                "title": "Analysis Results",
            }

        first_result = results[0]

        rows = first_result.get(
            "results",
            [],
        )

        if not isinstance(rows, list) or not rows:

            return {
                "chart_type": "table",
                "title": "Analysis Results",
            }

        columns = list(
            rows[0].keys()
        )

        numeric_columns = []

        for column in columns:

            values = [
                row.get(column)
                for row in rows
                if row.get(column) is not None
            ]

            if values and all(
                isinstance(
                    value,
                    (int, float),
                )
                and not isinstance(
                    value,
                    bool,
                )
                for value in values
            ):

                numeric_columns.append(
                    column
                )

        dimension_columns = [
            column
            for column in columns
            if column not in numeric_columns
        ]

        question_lower = question.lower()

        time_keywords = [
            "month",
            "monthly",
            "week",
            "weekly",
            "year",
            "yearly",
            "date",
            "daily",
            "over time",
            "trend",
        ]

        if (
            dimension_columns
            and numeric_columns
            and any(
                keyword in question_lower
                for keyword in time_keywords
            )
        ):

            return {
                "chart_type": "line",
                "x_axis": dimension_columns[0],
                "y_axis": numeric_columns[0],
                "title": question,
            }

        if (
            dimension_columns
            and numeric_columns
        ):

            return {
                "chart_type": "bar",
                "x_axis": dimension_columns[0],
                "y_axis": numeric_columns[0],
                "title": question,
            }

        return {
            "chart_type": "table",
            "title": question,
        }
