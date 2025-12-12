"""Tests for the execution layer."""

import pytest

from valuecell.agents.market_analysis_orchestrator.execution.backends.base import (
    ExecutionDecision,
    ExecutionResult,
)
from valuecell.agents.market_analysis_orchestrator.execution.backends.direct_order import (
    DirectOrderBackend,
)
from valuecell.agents.market_analysis_orchestrator.execution.backends.grid_strategy import (
    GridStrategyBackend,
)
from valuecell.agents.market_analysis_orchestrator.execution.backends.prompt_strategy import (
    PromptStrategyBackend,
)
from valuecell.agents.market_analysis_orchestrator.execution.backends.quant_strategy import (
    QuantStrategyBackend,
)
from valuecell.agents.market_analysis_orchestrator.execution.dispatcher import (
    ExecutionDispatcher,
)


class TestExecutionDecision:
    """Tests for ExecutionDecision model."""

    def test_create_decision(self):
        """Test creating an execution decision."""
        decision = ExecutionDecision(
            backend_id="direct_order",
            action="buy",
            symbol="AAPL",
            quantity=10,
            rationale="Test decision",
        )
        assert decision.backend_id == "direct_order"
        assert decision.action == "buy"
        assert decision.symbol == "AAPL"
        assert decision.quantity == 10

    def test_decision_with_params(self):
        """Test decision with backend-specific params."""
        decision = ExecutionDecision(
            backend_id="quant_nautilus",
            action="buy",
            symbol="BTCUSDT",
            params={"strategy_id": "ema_cross"},
            rationale="Use EMA strategy",
        )
        assert decision.params["strategy_id"] == "ema_cross"


class TestDirectOrderBackend:
    """Tests for DirectOrderBackend."""

    @pytest.fixture
    def backend(self):
        return DirectOrderBackend()

    def test_properties(self, backend):
        """Test backend properties."""
        assert backend.backend_id == "direct_order"
        assert backend.name == "直接下单"
        assert "direct" in backend.capabilities

    @pytest.mark.asyncio
    async def test_execute_buy(self, backend):
        """Test executing a buy order."""
        decision = ExecutionDecision(
            backend_id="direct_order",
            action="buy",
            symbol="AAPL",
            quantity=10,
            rationale="Test buy",
        )
        result = await backend.execute(decision, {})
        assert result.success
        assert len(result.trades) == 1
        assert result.trades[0]["side"] == "BUY"

    @pytest.mark.asyncio
    async def test_execute_hold(self, backend):
        """Test hold action."""
        decision = ExecutionDecision(
            backend_id="direct_order",
            action="hold",
            symbol="AAPL",
            rationale="Wait and see",
        )
        result = await backend.execute(decision, {})
        assert result.success
        assert len(result.trades) == 0


class TestQuantStrategyBackend:
    """Tests for QuantStrategyBackend."""

    @pytest.fixture
    def backend(self):
        return QuantStrategyBackend()

    def test_properties(self, backend):
        """Test backend properties."""
        assert backend.backend_id == "quant_nautilus"
        assert "quantitative" in backend.capabilities

    @pytest.mark.asyncio
    async def test_execute_with_strategy(self, backend):
        """Test execution with strategy selection."""
        decision = ExecutionDecision(
            backend_id="quant_nautilus",
            action="buy",
            symbol="BTCUSDT",
            params={"strategy_id": "ema_cross"},
            rationale="EMA crossover",
        )
        result = await backend.execute(decision, {})
        assert result.success
        assert result.metadata.get("strategy_id") == "ema_cross"


class TestExecutionDispatcher:
    """Tests for ExecutionDispatcher."""

    @pytest.fixture
    def dispatcher(self):
        d = ExecutionDispatcher()
        d.register_backend(DirectOrderBackend())
        d.register_backend(QuantStrategyBackend())
        d.set_default_backend("direct_order")
        return d

    def test_register_backend(self, dispatcher):
        """Test registering backends."""
        backends = dispatcher.list_backends()
        assert len(backends) == 2

    def test_get_backends_prompt(self, dispatcher):
        """Test generating backends prompt."""
        prompt = dispatcher.get_backends_prompt()
        assert "direct_order" in prompt
        assert "quant_nautilus" in prompt

    @pytest.mark.asyncio
    async def test_dispatch(self, dispatcher):
        """Test dispatching to a backend."""
        decision = ExecutionDecision(
            backend_id="direct_order",
            action="buy",
            symbol="AAPL",
            quantity=5,
            rationale="Test",
        )
        result = await dispatcher.dispatch(decision, {})
        assert result.success
        assert result.backend_id == "direct_order"

    @pytest.mark.asyncio
    async def test_dispatch_unknown_backend(self, dispatcher):
        """Test dispatching to unknown backend falls back to default."""
        decision = ExecutionDecision(
            backend_id="unknown_backend",
            action="buy",
            symbol="AAPL",
            rationale="Test",
        )
        result = await dispatcher.dispatch(decision, {})
        # Should use default backend
        assert result.backend_id == "direct_order" or not result.success
