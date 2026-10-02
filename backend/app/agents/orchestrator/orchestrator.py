from typing import Any

from app.agents.orchestrator.state import AnalysisState
from app.agents.planner.planner import PlannerAgent
from app.agents.sql.sql_agent import SQLAgent
from app.agents.validator.validator import AnalysisValidator
from app.services.llm import LLMService


class AnalysisOrchestrator:

    def __init__(self) -> None:

        llm = LLMService()

        self.planner = PlannerAgent(llm)
        self.sql_agent = SQLAgent(llm)
        self.validator = AnalysisValidator()

    async def create_plan(
        self,
        dataset_id: str,
        question: str,
        dataset_profile: dict[str, Any],
    ) -> AnalysisState:

        state = AnalysisState(
            dataset_id=dataset_id,
            question=question,
            dataset_profile=dataset_profile,
        )

        state.plan = await self.planner.create_plan(
            question=question,
            dataset_profile=dataset_profile,
        )

        return state

    async def analyze(
        self,
        dataset_id: str,
        question: str,
        dataset_profile: dict[str, Any],
        dataframe,
    ) -> AnalysisState:

        state = AnalysisState(
            dataset_id=dataset_id,
            question=question,
            dataset_profile=dataset_profile,
        )

        # Initial plan
        state.plan = await self.planner.create_plan(
            question=question,
            dataset_profile=dataset_profile,
        )

        while state.retry_count <= state.max_retries:

            state.results = []
            state.errors = []

            try:

                for step in state.plan.get("steps", []):

                    tool = step.get("tool")
                    description = step.get(
                        "description",
                        "",
                    )

                    if tool == "sql":

                        result = await self.sql_agent.execute(
                            task=description,
                            dataset_profile=dataset_profile,
                            dataframe=dataframe,
                        )

                        validation = self.validator.validate(
                            query=result["query"],
                            results=result["results"],
                        )

                        if not validation["valid"]:

                            state.errors.extend(
                                validation["errors"]
                            )

                            raise ValueError(
                                "Analysis validation failed."
                            )

                        state.results.append(result)

                    else:

                        state.errors.append(
                            f"Unsupported tool: {tool}"
                        )

                return state

            except Exception as exc:

                state.retry_count += 1

                state.errors.append(str(exc))

                if state.retry_count > state.max_retries:
                    break

                # Re-plan after failure
                state.plan = await self.planner.create_plan(
                    question=question,
                    dataset_profile=dataset_profile,
                )

        return state