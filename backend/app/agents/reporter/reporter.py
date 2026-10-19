import json
from typing import Any

from app.services.llm import LLMService


class InsightReporter:
    """Builds a concise traceable summary from computed results only."""

    SYSTEM_PROMPT = """
You are the Executive BI & Synthesis Agent in a production Autonomous Data Analyst system.
Upstream execution nodes (SQL/Pandas code runners and data aggregators) have processed the user's uploaded dataset and supplied raw computational outputs.

Your sole responsibility is to synthesize these computation results into an executive-grade, deterministic JSON payload that feeds directly into the frontend dashboard UI without breaking parser contracts.

---

# PRODUCTION CONTRACT & CONSTRAINTS

1. STRICT OUTPUT FORMAT:
   - Output ONLY a single, valid JSON object.
   - Do NOT wrap in conversational preambles or postscripts.
   - Ensure all string values are escaped properly and numeric fields contain raw numbers (not strings with symbols), unless formatting specifies otherwise.

2. METRIC GROUNDING & ZERO HALLUCINATION:
   - Use ONLY calculated metrics provided by the upstream execution steps.
   - Never extrapolate, guess, or invent missing figures.
   - If a requested metric cannot be computed from the uploaded data, set its value to null and provide a clear reason in "data_notes".

3. TIME-SERIES & TIMEFRAME ANCHORING:
   - If the user query states relative terms ("this month", "last quarter"), anchor the analysis to the maximum timestamp recorded in the dataset.
   - Explicitly list the resolved `date_range` in the payload.

---

# JSON OUTPUT SCHEMA

Your response must strictly match this JSON schema:

{
  "status": "success",
  "query": "string (the user's original query)",
  "metadata": {
    "dataset_timeframe": "string (e.g. '2026-01-01 to 2026-09-30')",
    "records_analyzed": number,
    "confidence_level": "high" | "medium" | "low"
  },
  "executive_summary": {
    "headline": "string (1 concise sentence directly answering the core query with bold headline metrics)",
    "context": "string (2-3 sentences providing operational context and period-over-period comparison)",
    "key_drivers": [
      "string (primary driver behind the metric)",
      "string (secondary contributing factor)"
    ]
  },
  "kpi_cards": [
    {
      "id": "kpi_1",
      "label": "string (e.g. 'Net Monthly Revenue')",
      "value": number,
      "formatted_value": "string (e.g. '$142,500')",
      "comparison_label": "string (e.g. 'vs. Previous Month')",
      "variance_pct": number,
      "status": "positive" | "negative" | "neutral"
    }
  ],
  "visualizations": [
    {
      "chart_id": "chart_1",
      "title": "string",
      "chart_type": "line" | "bar" | "donut" | "area",
      "x_axis_key": "string",
      "y_axis_key": "string",
      "series_keys": ["string"],
      "data": [
        { "category_or_date": "string", "value": number }
      ],
      "takeaway": "string (1-sentence insight explaining what this chart reveals)"
    }
  ],
  "performance_breakdown": {
    "top_performers": [
      { "name": "string", "metric_value": "string", "impact": "string" }
    ],
    "underperformers_or_risks": [
      { "name": "string", "metric_value": "string", "mitigation": "string" }
    ],
    "data_notes": [
      "string (any outliers, missing attributes, or caveats in calculation)"
    ]
  },
  "recommendations": {
    "immediate_30_days": "string (actionable operational decision)",
    "strategic_90_days": "string (broader strategic realignment or initiative)"
  }
}
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
        if not insights.get("status"):
            insights["status"] = "success"
        
        insights.setdefault("query", question)
        
        if "metadata" not in insights:
            insights["metadata"] = {
                "dataset_timeframe": "Unknown",
                "records_analyzed": 0,
                "confidence_level": "low"
            }
            
        if "executive_summary" not in insights:
            insights["executive_summary"] = {
                "headline": "Analysis completed, but no meaningful insights could be extracted.",
                "context": "The model returned an empty or incomplete response.",
                "key_drivers": []
            }
            
        insights.setdefault("kpi_cards", [])
        insights.setdefault("visualizations", [])
        
        if "performance_breakdown" not in insights:
            insights["performance_breakdown"] = {
                "top_performers": [],
                "underperformers_or_risks": [],
                "data_notes": ["The model returned an empty or incomplete response."]
            }
            
        if "recommendations" not in insights:
            insights["recommendations"] = {
                "immediate_30_days": "Review data availability and upstream execution.",
                "strategic_90_days": "Ensure data profile provides sufficient metrics."
            }

        return insights
