from typing import Any

from app.agents.validator.semantic_validator import (
    SemanticValidator,
)
from app.services.llm import LLMService


class AnalysisValidator:

    def __init__(self) -> None:

        llm = LLMService()

        self.semantic_validator = (
            SemanticValidator(llm)
        )

    def validate_technical(
        self,
        query: str,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        errors: list[str] = []

        if not query or not query.strip():

            errors.append(
                "Generated SQL query is empty."
            )

        normalized = query.strip().upper()

        if not normalized.startswith("SELECT"):

            errors.append(
                "Only SELECT queries are allowed."
            )

        if results is None:

            errors.append(
                "No result returned from SQL execution."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    async def validate_semantic(
        self,
        question: str,
        plan: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        return await (
            self.semantic_validator.validate(
                question=question,
                plan=plan,
                results=results,
            )
        )