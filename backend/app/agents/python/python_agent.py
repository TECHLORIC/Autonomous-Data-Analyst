from typing import Any

import pandas as pd

from app.data.access import DatasetAccess


class PythonAnalysisAgent:

    def __init__(self, llm=None) -> None:
        self.dataset_access = DatasetAccess()
        self.llm = llm

    def load_dataset(
        self,
        dataset_id: str,
        file_path: str = "",
    ) -> pd.DataFrame:
        return self.dataset_access.load_dataframe(
            dataset_id, file_path=file_path
        )

    async def execute_sandbox(self, task: str, dataset_profile: dict, file_path: str) -> dict[str, Any]:
        """
        Generates Python pandas code using the LLM and executes it in a Docker Sandbox.
        """
        if not self.llm:
            raise ValueError("LLMService is required for arbitrary Python execution.")
            
        import json
        
        system_prompt = """
You are an expert Data Scientist and Machine Learning Engineer. Write Python 3 code using pandas, scikit-learn, scipy, or statsmodels to solve the analysis task.

CRITICAL RULES:
1. The dataset will be mounted as a file in the same directory.
2. The file extension could be .csv or .parquet. You should use `os.listdir('.')` to find the exact filename starting with 'dataset.'
3. DO NOT use plt.show() or graphical popups.
4. The output must be written to a file named exactly 'result.json' in the current directory as a JSON array or object.
5. All numpy types must be converted to native Python types before dumping to JSON.
6. Do NOT wrap your response in markdown formatting or ```python ... ```. Output ONLY the raw valid Python code.
7. Available libraries: pandas, numpy, scikit-learn, scipy, statsmodels.
"""

        user_prompt = f"""
Dataset Profile:
{json.dumps(dataset_profile, default=str)}

Analysis Task:
{task}

Write the raw Python script to complete this task and save results to 'result.json'.
"""
        
        code = await self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        
        # Remove any markdown formatting if the LLM ignored instructions
        if code.startswith("```"):
            lines = code.split("\n")
            if len(lines) > 2:
                code = "\n".join(lines[1:-1])

        from app.services.sandbox import PythonSandbox
        sandbox = PythonSandbox()
        
        result_payload = sandbox.execute(code=code, dataset_path=file_path)
        
        return {
            "task": task,
            "tool": "python",
            "query": code,
            "results": result_payload.get("result") or [],
            "sandbox_logs": result_payload.get("stdout", ""),
            "success": result_payload.get("success", False),
            "error": result_payload.get("error")
        }

    def describe_numeric_column(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> dict[str, Any]:

        if column not in dataframe.columns:

            raise ValueError(
                f"Column '{column}' does not exist."
            )

        if not pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):

            raise ValueError(
                f"Column '{column}' is not numeric."
            )

        series = dataframe[column].dropna()

        if series.empty:

            raise ValueError(
                f"Column '{column}' contains "
                f"no usable values."
            )

        return {
            "column": column,
            "count": int(series.count()),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
        }

    def correlation(
        self,
        dataframe: pd.DataFrame,
        column_a: str,
        column_b: str,
    ) -> dict[str, Any]:

        for column in [
            column_a,
            column_b,
        ]:

            if column not in dataframe.columns:

                raise ValueError(
                    f"Column '{column}' does not exist."
                )

            if not pd.api.types.is_numeric_dtype(
                dataframe[column]
            ):

                raise ValueError(
                    f"Column '{column}' must be numeric."
                )

        correlation = (
            dataframe[
                [column_a, column_b]
            ]
            .corr()
            .iloc[0, 1]
        )

        return {
            "column_a": column_a,
            "column_b": column_b,
            "correlation": float(correlation),
        }

    def detect_outliers(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> dict[str, Any]:

        if column not in dataframe.columns:

            raise ValueError(
                f"Column '{column}' does not exist."
            )

        if not pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):

            raise ValueError(
                f"Column '{column}' must be numeric."
            )

        series = dataframe[column].dropna()

        if series.empty:

            raise ValueError(
                f"Column '{column}' contains "
                f"no usable values."
            )

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr

        upper_bound = q3 + 1.5 * iqr

        outliers = series[
            (series < lower_bound)
            | (series > upper_bound)
        ]

        return {
            "column": column,
            "outlier_count": int(
                len(outliers)
            ),
            "lower_bound": float(
                lower_bound
            ),
            "upper_bound": float(
                upper_bound
            ),
            "outliers": [
                float(value)
                for value in outliers.tolist()
            ],
        }