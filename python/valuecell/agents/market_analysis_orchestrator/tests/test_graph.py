"""Tests for the analysis graph."""

import pytest

from valuecell.agents.market_analysis_orchestrator.graph.analysis_graph import (
    AnalysisGraph,
)
from valuecell.agents.market_analysis_orchestrator.internal_agents.states import (
    AgentState,
    create_initial_state,
)


class TestAgentState:
    """Tests for AgentState."""

    def test_create_initial_state(self):
        """Test creating initial state."""
        state = create_initial_state(
            ticker="000001.SZ",
            trade_date="2025-12-12",
            market_type="china",
        )
        assert state["company_of_interest"] == "000001.SZ"
        assert state["trade_date"] == "2025-12-12"
        assert state["market_type"] == "china"
        assert state["messages"] == []

    def test_initial_state_defaults(self):
        """Test that initial state has correct defaults."""
        state = create_initial_state("AAPL", "2025-12-12", "us")
        assert state["market_report"] is None
        assert state["fundamentals_report"] is None
        assert state["market_tool_call_count"] == 0


class TestAnalysisGraph:
    """Tests for AnalysisGraph."""

    @pytest.fixture
    def graph(self):
        return AnalysisGraph(selected_analysts=["market", "fundamentals"])

    def test_initialization(self, graph):
        """Test graph initialization."""
        assert graph.selected_analysts == ["market", "fundamentals"]
        assert graph._state is None

    @pytest.mark.asyncio
    async def test_propagate(self, graph):
        """Test running analysis propagation."""
        result = await graph.propagate(
            ticker="000001.SZ",
            trade_date="2025-12-12",
            market_type="china",
        )
        assert "market_analysis" in result
        assert "fundamentals_analysis" in result

    @pytest.mark.asyncio
    async def test_propagate_sets_state(self, graph):
        """Test that propagate sets internal state."""
        await graph.propagate("AAPL", "2025-12-12", "us")
        assert graph._state is not None
        assert graph._state["company_of_interest"] == "AAPL"

    @pytest.mark.asyncio
    async def test_propagate_stream(self, graph):
        """Test streaming analysis."""
        steps = []
        async for node_name, output in graph.propagate_stream(
            "BTCUSDT", "2025-12-12", "china"
        ):
            steps.append(node_name)

        # Should have analyst nodes + researcher nodes
        assert "Market Analyst" in steps
        assert "Fundamentals Analyst" in steps
        assert "Bull Researcher" in steps
        assert "Bear Researcher" in steps
        assert "Research Manager" in steps

    def test_get_analysis_report_empty(self, graph):
        """Test getting report when no analysis has run."""
        report = graph.get_analysis_report()
        assert report == {}

    @pytest.mark.asyncio
    async def test_get_analysis_report_after_propagate(self, graph):
        """Test getting report after analysis."""
        await graph.propagate("AAPL", "2025-12-12", "us")
        report = graph.get_analysis_report()
        assert "market_analysis" in report
        assert report["market_analysis"] is not None

    def test_get_risk_assessment_empty(self, graph):
        """Test getting risk assessment when no analysis has run."""
        assessment = graph.get_risk_assessment()
        assert assessment == {}

    @pytest.mark.asyncio
    async def test_get_risk_assessment_after_propagate(self, graph):
        """Test getting risk assessment after analysis."""
        await graph.propagate("AAPL", "2025-12-12", "us")
        assessment = graph.get_risk_assessment()
        assert "risk_level" in assessment
