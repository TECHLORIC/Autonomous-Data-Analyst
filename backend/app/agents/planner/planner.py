import json
from typing import Any

from app.services.llm import LLMService


class PlannerAgent:

    SYSTEM_PROMPT = """
You are the planning component of an autonomous data analyst.

Your job is to convert a user's analytical question into
a small sequence of precise analysis steps.

You DO NOT execute SQL.
You DO NOT execute Python.

Available tools:

SQL:
- filtering
- grouping
- aggregation
- sorting
- totals
- averages
- counts
- joins
- comparisons

PYTHON:
- descriptive statistics
- correlation
- outlier detection
- clustering
- forecasting
- regression
- hypothesis testing

Rules:

1. Use SQL for normal tabular aggregation (filtering, grouping, counts).
2. Use Python for statistical analysis, machine learning, clustering, forecasting, and regressions.
3. Never invent column names.
4. Only use columns from the dataset profile.
5. Keep the plan as small as possible (2 to 4 steps maximum).
6. Return ONLY valid JSON.
7. DO NOT generate steps for creating charts, plots, or visualizations. The UI automatically handles charting.
8. When the user asks for a comprehensive report, 360-degree insights, or general dataset overview:
   - Formulate 2 to 4 focused aggregation steps covering key business perspectives:
     * Step 1: Overall KPIs (compute SUM of key metric like sales/revenue, COUNT of orders/customers, AVG).
     * Step 2: Product / Category breakdown (GROUP BY primary category or product line, ORDER BY sum DESC LIMIT 10).
     * Step 3: Geographic or Segment breakdown (GROUP BY territory/country/region/dealsize, ORDER BY sum DESC LIMIT 10).
     * Step 4: Temporal trend (if date/year/month is present, group by timeframe/year/month).
   - ALWAYS specify aggregation (SUM, COUNT, AVG, GROUP BY) in SQL step descriptions. NEVER select unbounded raw rows without aggregation.

For Python operations, use one of:

describe
correlation
detect_outliers
clustering
forecasting
regression
hypothesis_testing

Required format:

{
    "goal": "string",
    "steps": [
        {
            "step": 1,
            "description": "string",
            "tool": "sql",
            "operation": "aggregate"
        }
    ]
}

Python example:

{
    "goal": "Find revenue outliers",
    "steps": [
        {
            "step": 1,
            "description": "Detect outliers in Revenue",
            "tool": "python",
            "operation": "detect_outliers",
            "columns": ["Revenue"]
        }
    ]
}
"""

    def __init__(
        self,
        llm: LLMService,
    ) -> None:
        self.llm = llm

    async def create_plan(
        self,
        question: str,
        dataset_profile: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = f"""
User question:

{question}

Dataset profile:

{json.dumps(
    dataset_profile,
    default=str,
)}

Create the analysis plan.
"""

        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        try:
            plan = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Planner returned invalid JSON."
            ) from exc

        self._validate_plan(plan)

        return plan

    def _validate_plan(
        self,
        plan: dict[str, Any],
    ) -> None:

        if "goal" not in plan:
            raise ValueError(
                "Planner response is missing 'goal'."
            )

        if "steps" not in plan:
            raise ValueError(
                "Planner response is missing 'steps'."
            )

        if not isinstance(
            plan["steps"],
            list,
        ):
            raise ValueError(
                "'steps' must be a list."
            )

        for step in plan["steps"]:

            if "tool" not in step:
                raise ValueError(
                    "Every step must specify a tool."
                )

            if step["tool"] not in {
                "sql",
                "python",
            }:
                raise ValueError(
                    f"Unsupported tool: {step['tool']}"
                )
