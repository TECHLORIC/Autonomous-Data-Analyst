import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.reporter.reporter import InsightReporter
from app.services.llm import LLMService

@pytest.mark.anyio
async def test_reporter_describes_computed_rows() -> None:
    mock_llm = MagicMock(spec=LLMService)
    mock_llm.generate = AsyncMock(return_value='{"executive_answer": "It is good.", "key_findings": [], "trends_and_anomalies": [], "caveats": [], "next_questions": []}')
    
    reporter = InsightReporter(llm=mock_llm)
    insights = await reporter.generate(
        question="Is it good?",
        plan={},
        results=[{"tool": "sql", "results": [{"total": 10}]}]
    )

    assert insights["executive_answer"] == "It is good."
    assert mock_llm.generate.call_count == 1
