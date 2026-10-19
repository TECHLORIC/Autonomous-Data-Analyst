import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.reporter.reporter import InsightReporter
from app.services.llm import LLMService

@pytest.mark.anyio
async def test_reporter_describes_computed_rows() -> None:
    mock_llm = MagicMock(spec=LLMService)
    
    # Mocking the new Executive BI schema
    mock_payload = '''
    {
      "status": "success",
      "query": "Is it good?",
      "executive_summary": {
        "headline": "It is good.",
        "context": "Metrics indicate positive performance."
      }
    }
    '''
    mock_llm.generate = AsyncMock(return_value=mock_payload)
    
    reporter = InsightReporter(llm=mock_llm)
    insights = await reporter.generate(
        question="Is it good?",
        plan={},
        results=[{"tool": "sql", "results": [{"total": 10}]}]
    )

    assert insights["executive_summary"]["headline"] == "It is good."
    assert "kpi_cards" in insights  # Fallback logic should add this
    assert mock_llm.generate.call_count == 1

