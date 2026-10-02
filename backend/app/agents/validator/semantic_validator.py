import json
from typing import Any

from app.services.llm import LLMService


class SemanticValidator:

    SYSTEM_PROMPT = """
You are a semantic validation component for an
autonomous data analyst.

Your job is to determine whether the analysis results
actually answer the user's question.

Check:

1. Does the result address the user's question?
2. Were appropriate columns analyzed?
3. Is the result meaningful?
4. Is the result empty or obviously incomplete?
5. Does the result contradict the requested analysis?

Return ONLY valid JSON.

Required format:

{
    "valid": true,
    "reason": "short explanation",
    "suggestion": "what should be changed if invalid"
}
"""

    def __init__(
        self,
        llm: LLMService,
    ) -> None:

        self.llm = llm

    async def validate(
        self,
        question: str,
        plan: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        prompt = f"""
User question:

{question}

Analysis plan:

{json.dumps(
    plan,
    indent=2,
    default=str,
)}

Analysis results:

{json.dumps(
    results,
    indent=2,
    default=str,
)}

Determine whether the analysis correctly answers
the user's question.
"""

        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        try:

            validation = json.loads(response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Semantic validator returned invalid JSON."
            ) from exc

        return validation