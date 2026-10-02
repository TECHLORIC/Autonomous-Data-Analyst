import json
from typing import Any

from app.services.llm import LLMService


class InsightReporter:
    """Builds a concise traceable summary from computed results only."""

    SYSTEM_PROMPT = """
You are an Insight Reporter for an autonomous data analyst.
Your job is to generate a comprehensive human-readable report based ONLY on the computed results provided.
Do NOT invent or hallucinate numbers. Every numerical statement must be traceable to the results.

Generate a JSON object containing the following fields:
- "executive_answer": A concise paragraph directly answering the user's question.
- "key_findings": A list of the most important findings and supporting numbers.
- "trends_and_anomalies": A list of notable trends or anomalies, if any.
- "caveats": A list of important limitations or caveats about the analysis.
- "next_questions": A list of recommended follow-up questions.

Return ONLY valid JSON.
"""

    def __init__(self, llm: LLMService | None = None) -> None:
        # Allow passing an existing LLMService, or instantiate one
        self.llm = llm if llm is not None else LLMService()

    async def generate(
        self,
        question: str,
        plan: dict[str, Any],
        results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        prompt = f"""
User question:
{question}

Analysis plan:
{json.dumps(plan, indent=2, default=str)}

Analysis results:
{json.dumps(results, indent=2, default=str)}

Generate the insights based on the analysis results above.
"""
        response = await self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        try:
            insights = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Insight Reporter returned invalid JSON."
            ) from exc

        # Ensure required keys exist so the frontend renders properly
        if not insights.get("executive_answer"):
            insights["executive_answer"] = "Analysis completed, but no meaningful insights could be extracted (the query may have returned no data)."
            
        insights.setdefault("key_findings", [])
        insights.setdefault("trends_and_anomalies", [])
        insights.setdefault("caveats", ["The model returned an empty or incomplete response."])
        insights.setdefault("next_questions", [])

        return insights
