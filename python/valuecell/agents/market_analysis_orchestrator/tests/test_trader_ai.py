"""Tests for Trader AI."""

import pytest

from valuecell.agents.market_analysis_orchestrator.execution.backends.direct_order import (
    DirectOrderBackend,
)
from valuecell.agents.market_analysis_orchestrator.execution.dispatcher import (
    ExecutionDispatcher,
)
from valuecell.agents.market_analysis_orchestrator.internal_agents.trader.trader_ai import (
    TraderAI,
)


class TestTraderAI:
    """Tests for Trader AI decision engine."""

    @pytest.fixture
    def dispatcher(self):
        d = ExecutionDispatcher()
        d.register_backend(DirectOrderBackend())
        d.set_default_backend("direct_order")
        return d

    @pytest.fixture
    def trader(self, dispatcher):
        # Use None for LLM, will fall back to default response
        return TraderAI(llm=None, dispatcher=dispatcher)

    @pytest.mark.asyncio
    async def test_make_decision_no_llm(self, trader):
        """Test decision making without LLM falls back gracefully."""
        decision = await trader.make_decision(
            analysis_report={"market_analysis": "bullish"},
            risk_assessment={"risk_level": "low"},
            market_context={"symbol": "AAPL"},
        )
        # Without LLM, returns default response with UNKNOWN symbol
        assert decision.symbol == "UNKNOWN"
        assert decision.action == "hold"
        assert decision.backend_id == "direct_order"

    def test_build_decision_prompt(self, trader):
        """Test prompt building includes all sections."""
        prompt = trader._build_decision_prompt(
            analysis_report={"test": "data"},
            risk_assessment={"risk": "low"},
            market_context={"symbol": "BTCUSDT"},
        )
        assert "ANALYSIS REPORT" in prompt
        assert "RISK ASSESSMENT" in prompt
        assert "AVAILABLE EXECUTION BACKENDS" in prompt

    def test_parse_decision_valid_json(self, trader):
        """Test parsing valid JSON response."""
        response = '''
        {
            "action": "buy",
            "backend_id": "direct_order",
            "symbol": "AAPL",
            "quantity": 10,
            "rationale": "Strong buy signal"
        }
        '''
        decision = trader._parse_decision(response, {"symbol": "DEFAULT"})
        assert decision.action == "buy"
        assert decision.backend_id == "direct_order"
        assert decision.symbol == "AAPL"

    def test_parse_decision_json_in_code_block(self, trader):
        """Test parsing JSON wrapped in markdown code block."""
        response = '''Here is my decision:
```json
{
    "action": "sell",
    "backend_id": "quant_nautilus",
    "symbol": "BTCUSDT",
    "rationale": "Bearish divergence"
}
```
'''
        decision = trader._parse_decision(response, {"symbol": "DEFAULT"})
        assert decision.action == "sell"
        assert decision.backend_id == "quant_nautilus"

    def test_parse_decision_invalid_json(self, trader):
        """Test parsing invalid JSON falls back gracefully."""
        response = "This is not valid JSON at all"
        decision = trader._parse_decision(response, {"symbol": "FALLBACK"})
        assert decision.symbol == "FALLBACK"
        assert decision.action == "hold"
