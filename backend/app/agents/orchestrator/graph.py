from typing import Any

import pandas as pd
from langgraph.graph import END, START, StateGraph

from app.agents.orchestrator.state import AnalysisState
from app.agents.planner.planner import PlannerAgent
from app.agents.reporter.reporter import InsightReporter
from app.agents.python.python_agent import (
    PythonAnalysisAgent,
)
from app.agents.sql.sql_agent import SQLAgent
from app.agents.validator.validator import (
    AnalysisValidator,
)
from app.agents.visualization.chart_selector import (
    ChartSelector,
)
from app.services.llm import LLMService


class AutonomousAnalysisGraph:

    def __init__(self) -> None:

        # -------------------------
        # Services / agents
        # -------------------------

        llm = LLMService()

        self.planner = PlannerAgent(llm)

        self.sql_agent = SQLAgent(llm)

        self.python_agent = (
            PythonAnalysisAgent(llm)
        )

        self.validator = (
            AnalysisValidator()
        )

        self.chart_selector = (
            ChartSelector()
        )
        self.reporter = InsightReporter(llm)

        # -------------------------
        # Build graph
        # -------------------------

        graph = StateGraph(
            AnalysisState
        )

        # Nodes
        graph.add_node(
            "planner",
            self.planner_node,
        )

        graph.add_node(
            "tool_router",
            self.tool_router_node,
        )

        graph.add_node(
            "sql_agent",
            self.sql_node,
        )

        graph.add_node(
            "python_agent",
            self.python_node,
        )

        graph.add_node(
            "validator",
            self.validator_node,
        )

        graph.add_node(
            "replan",
            self.replan_node,
        )

        graph.add_node(
            "visualization",
            self.visualization_node,
        )
        graph.add_node("reporter", self.reporter_node)

        # -------------------------
        # Graph flow
        # -------------------------

        graph.add_edge(
            START,
            "planner",
        )

        graph.add_edge(
            "planner",
            "tool_router",
        )

        graph.add_conditional_edges(
            "tool_router",
            self.tool_router,
            {
                "sql": "sql_agent",
            },
        )

        graph.add_edge(
            "sql_agent",
            "validator",
        )

        graph.add_conditional_edges(
            "validator",
            self.validation_router,
            {
                "pass": "visualization",
                "retry": "replan",
                # After retries are exhausted, still report best-effort results
                # instead of ending with an empty dashboard.
                "stop": "visualization",
            },
        )

        graph.add_edge(
            "replan",
            "tool_router",
        )

        graph.add_edge(
            "visualization",
            "reporter",
        )
        graph.add_edge("reporter", END)

        # -------------------------
        # Compile
        # -------------------------

        self.graph = graph.compile()

    # ==================================================
    # PLANNER
    # ==================================================

    async def planner_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        plan = await (
            self.planner.create_plan(
                question=state.question,
                dataset_profile=(
                    state.dataset_profile
                ),
            )
        )

        return {
            "plan": plan,
            "status": "planned",
            "current_step": 1,
        }

    # ==================================================
    # TOOL ROUTER
    # ==================================================

    def tool_router_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        return {
            "status": "routing"
        }

    def tool_router(
        self,
        state: AnalysisState,
    ) -> str:

        steps = state.plan.get(
            "steps",
            [],
        )

        if not steps:

            return "sql"

        # The executor processes every ordered plan step. Routing only selects
        # that controlled execution node; it must not discard later steps.
        return "sql"

    # ==================================================
    # SQL
    # ==================================================

    async def sql_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        results = []

        steps = state.plan.get(
            "steps",
            [],
        )

        for step in steps:
            tool = step.get("tool")
            if tool == "python":
                continue
            if tool != "sql":
                raise ValueError(f"Unsupported analysis tool: {tool}")

            description = step.get(
                "description",
                "",
            )

            try:
                result = await (
                    self.sql_agent.execute(
                        task=description,
                        dataset_profile=(
                            state.dataset_profile
                        ),
                        dataset_id=(
                            state.dataset_id
                        ),
                        file_path=state.file_path,
                    )
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "task": description,
                    "tool": "sql",
                    "results": [],
                    "query": "",
                    "error": f"Execution failed: {str(e)}"
                })

        # SQL and Python steps can coexist in one plan. Execute the Python
        # subset before validation so the complete plan is evaluated.
        if any(step.get("tool") == "python" for step in steps):
            python_results = await self._execute_python_steps(state)
            results.extend(python_results)

        return {
            "results": results,
            "status": "sql_completed",
        }

    # ==================================================
    # PYTHON
    # ==================================================

    async def python_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        results = await self._execute_python_steps(state)

        return {
            "results": results,
            "status": "python_completed",
        }

    async def _execute_python_steps(
        self,
        state: AnalysisState,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        steps = state.plan.get(
            "steps",
            [],
        )

        python_steps = [step for step in steps if step.get("tool") == "python"]
        if not python_steps:
            return results

        dataframe = self.python_agent.load_dataset(
            state.dataset_id,
            file_path=state.file_path
        )

        # Python Steps Execution
        results = []
        for step in python_steps:
            description = step.get("description", "")
            description_lower = description.lower()

            try:
                # Deterministic Fallbacks
                if "correlation" in description_lower:
                    numeric_columns = [col for col in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[col])]
                    if len(numeric_columns) < 2:
                        raise ValueError("At least two numeric columns required for correlation.")
                    req = step.get("columns", [])
                    cols = [c for c in req if c in numeric_columns] or numeric_columns[:2]
                    res = self.python_agent.correlation(dataframe, cols[0], cols[1])
                    results.append({"task": description, "tool": "python", "results": [res], "query": "self.python_agent.correlation(...)"})
                    continue
                    
                elif "outlier" in description_lower:
                    numeric_columns = [col for col in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[col])]
                    if not numeric_columns:
                        raise ValueError("No numeric columns available.")
                    req = step.get("columns", [])
                    col = req[0] if req and req[0] in numeric_columns else numeric_columns[0]
                    res = self.python_agent.detect_outliers(dataframe, col)
                    results.append({"task": description, "tool": "python", "results": [res], "query": "self.python_agent.detect_outliers(...)"})
                    continue

                # Default: Execute Sandbox
                res = await self.python_agent.execute_sandbox(
                    task=description, 
                    dataset_profile=state.dataset_profile, 
                    file_path=state.file_path
                )
                results.append(res)
                
            except Exception as e:
                results.append({
                    "task": description,
                    "tool": "python",
                    "results": [],
                    "query": "",
                    "error": str(e)
                })

        return results

    # ==================================================
    # VALIDATOR
    # ==================================================

    async def validator_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        errors = []

        # --------------------------------
        # Technical validation
        # --------------------------------

        for result in state.results:
            
            if "error" in result and result["error"]:
                errors.append(result["error"])
                continue

            if "query" not in result:
                continue

            validation = (
                self.validator.validate_technical(
                    query=result["query"],
                    results=result.get(
                        "results",
                        [],
                    ),
                )
            )

            if not validation["valid"]:

                errors.extend(
                    validation["errors"]
                )

        # --------------------------------
        # Semantic validation
        # --------------------------------

        if not errors:

            semantic = (
                await self.validator
                .validate_semantic(
                    question=state.question,
                    plan=state.plan,
                    results=state.results,
                )
            )

            if not semantic.get(
                "valid",
                False,
            ):

                reason = semantic.get(
                    "reason",
                    "Analysis did not answer "
                    "the question.",
                )

                suggestion = semantic.get(
                    "suggestion",
                    "",
                )

                errors.append(reason)

                if suggestion:

                    errors.append(
                        f"Suggestion: {suggestion}"
                    )

        # --------------------------------
        # State update
        # --------------------------------

        if errors:

            return {
                "errors": errors,
                "retry_count": (
                    state.retry_count + 1
                ),
                "status": "validation_failed",
            }

        return {
            "errors": [],
            "status": "validated",
        }

    # ==================================================
    # VALIDATION ROUTER
    # ==================================================

    def validation_router(
        self,
        state: AnalysisState,
    ) -> str:

        if not state.errors:

            return "pass"

        if (
            state.retry_count
            < state.max_retries
        ):

            return "retry"

        return "stop"

    # ==================================================
    # REPLAN
    # ==================================================

    async def replan_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        previous_errors = "\n".join(
            state.errors
        )

        replanning_question = f"""
Original user question:

{state.question}

The previous analysis attempt failed
validation.

Validation feedback:

{previous_errors}

Create a corrected analysis plan.

Do not repeat the same mistake.
"""

        plan = await (
            self.planner.create_plan(
                question=replanning_question,
                dataset_profile=(
                    state.dataset_profile
                ),
            )
        )

        return {
            "plan": plan,
            "errors": [],
            "status": "replanned",
        }

    # ==================================================
    # VISUALIZATION
    # ==================================================

    async def visualization_node(
        self,
        state: AnalysisState,
    ) -> dict[str, Any]:

        chart = (
            self.chart_selector.select_chart(
                results=state.results,
                question=state.question,
            )
        )

        return {
            "visualizations": [chart],
            "status": "visualized",
        }

    async def reporter_node(self, state: AnalysisState) -> dict[str, Any]:
        insights = await self.reporter.generate(
            question=state.question,
            plan=state.plan,
            results=state.results
        )
        return {
            "insights": insights,
            "status": "completed",
        }

    # ==================================================
    # RUN
    # ==================================================

    async def run(
        self,
        dataset_id: str,
        question: str,
        dataset_profile: dict[str, Any],
        file_path: str = "",
    ) -> AnalysisState:
        """
        Runs the full autonomous analysis workflow.
        """
        # 1. Initialize State
        state = AnalysisState(
            dataset_id=dataset_id,
            file_path=file_path,
            question=question,
            dataset_profile=dataset_profile,
        )

        final_state = await self.graph.ainvoke(
            state
        )

        if isinstance(final_state, AnalysisState):
            return final_state

        return AnalysisState(
            dataset_id=final_state.get(
                "dataset_id",
                dataset_id,
            ),
            question=final_state.get(
                "question",
                question,
            ),
            dataset_profile=final_state.get(
                "dataset_profile",
                dataset_profile,
            ),
            plan=final_state.get(
                "plan",
                {},
            ),
            results=final_state.get(
                "results",
                [],
            ),
            visualizations=final_state.get(
                "visualizations",
                [],
            ),
            insights=final_state.get("insights", {}),
            errors=final_state.get(
                "errors",
                [],
            ),
            retry_count=final_state.get(
                "retry_count",
                0,
            ),
            max_retries=final_state.get(
                "max_retries",
                2,
            ),
            current_step=final_state.get(
                "current_step",
                0,
            ),
            status=final_state.get(
                "status",
                "completed",
            ),
        )

    async def stream(
        self,
        dataset_id: str,
        question: str,
        dataset_profile: dict,
        file_path: str = "",
    ):
        """
        Yields JSON events for SSE as the graph progresses.
        """
        import json
        state = AnalysisState(
            dataset_id=dataset_id,
            file_path=file_path,
            question=question,
            dataset_profile=dataset_profile,
        )

        async for event in self.graph.astream(state):
            # LangGraph astream returns dicts like: {'planner': {'plan': ...}}
            # We wrap it in a Server-Sent Event format string.
            yield f"data: {json.dumps(event)}\n\n"

