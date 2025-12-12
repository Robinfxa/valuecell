"""Tests for internal agents."""

import pytest

from valuecell.agents.market_analysis_orchestrator.internal_agents.analysts import (
    create_fundamentals_analyst,
    create_market_analyst,
    create_news_analyst,
    create_social_analyst,
    get_company_name,
    get_currency_info,
)
from valuecell.agents.market_analysis_orchestrator.internal_agents.researchers import (
    create_bear_researcher,
    create_bull_researcher,
    create_research_manager,
)
from valuecell.agents.market_analysis_orchestrator.internal_agents.risk_mgmt import (
    create_neutral_debater,
    create_risk_manager,
    create_risky_debater,
    create_safe_debater,
)


class TestAnalystHelpers:
    """Tests for analyst helper functions."""

    def test_get_company_name_us(self):
        """Test US stock name lookup."""
        assert get_company_name("AAPL", "us") == "苹果公司"
        assert get_company_name("TSLA", "us") == "特斯拉"
        assert get_company_name("UNKNOWN", "us") == "美股UNKNOWN"

    def test_get_company_name_hk(self):
        """Test HK stock name generation."""
        assert get_company_name("0700.HK", "hk") == "港股0700"

    def test_get_company_name_china(self):
        """Test China stock name generation."""
        result = get_company_name("000001.SZ", "china")
        assert "000001.SZ" in result

    def test_get_currency_info(self):
        """Test currency info for different markets."""
        assert get_currency_info("china")["currency_symbol"] == "¥"
        assert get_currency_info("us")["currency_symbol"] == "$"
        assert get_currency_info("hk")["currency_symbol"] == "HK$"


class TestAnalystNodes:
    """Tests for analyst node creation."""

    def test_create_market_analyst(self):
        """Test market analyst creation."""
        node = create_market_analyst(llm=None)
        assert callable(node)

    def test_create_fundamentals_analyst(self):
        """Test fundamentals analyst creation."""
        node = create_fundamentals_analyst(llm=None)
        assert callable(node)

    def test_create_news_analyst(self):
        """Test news analyst creation."""
        node = create_news_analyst(llm=None)
        assert callable(node)

    def test_create_social_analyst(self):
        """Test social analyst creation."""
        node = create_social_analyst(llm=None)
        assert callable(node)

    def test_analyst_node_execution(self):
        """Test executing analyst node without LLM."""
        node = create_market_analyst(llm=None)
        state = {
            "company_of_interest": "AAPL",
            "trade_date": "2025-12-12",
            "market_type": "us",
        }
        result = node(state)
        assert "market_report" in result
        assert "苹果" in result["market_report"] or "AAPL" in result["market_report"]


class TestResearcherNodes:
    """Tests for researcher node creation."""

    def test_create_bull_researcher(self):
        """Test bull researcher creation."""
        node = create_bull_researcher(llm=None)
        assert callable(node)

    def test_create_bear_researcher(self):
        """Test bear researcher creation."""
        node = create_bear_researcher(llm=None)
        assert callable(node)

    def test_create_research_manager(self):
        """Test research manager creation."""
        node = create_research_manager(llm=None)
        assert callable(node)

    def test_bull_node_execution(self):
        """Test executing bull researcher without LLM."""
        node = create_bull_researcher(llm=None)
        state = {
            "company_of_interest": "AAPL",
            "market_type": "us",
            "market_report": "技术面看好",
            "sentiment_report": "情绪乐观",
            "news_report": "无重大新闻",
            "fundamentals_report": "财务健康",
            "investment_debate_state": {"history": "", "count": 0},
        }
        result = node(state)
        assert "investment_debate_state" in result
        assert result["investment_debate_state"]["count"] == 1


class TestRiskManagementNodes:
    """Tests for risk management node creation."""

    def test_create_risky_debater(self):
        """Test risky debater creation."""
        node = create_risky_debater(llm=None)
        assert callable(node)

    def test_create_safe_debater(self):
        """Test safe debater creation."""
        node = create_safe_debater(llm=None)
        assert callable(node)

    def test_create_neutral_debater(self):
        """Test neutral debater creation."""
        node = create_neutral_debater(llm=None)
        assert callable(node)

    def test_create_risk_manager(self):
        """Test risk manager creation."""
        node = create_risk_manager(llm=None)
        assert callable(node)

    def test_risky_node_execution(self):
        """Test executing risky debater without LLM."""
        node = create_risky_debater(llm=None)
        state = {
            "market_report": "技术面看好",
            "sentiment_report": "情绪乐观",
            "news_report": "无重大新闻",
            "fundamentals_report": "财务健康",
            "trader_investment_plan": "建议买入",
            "risk_debate_state": {"history": "", "count": 0},
        }
        result = node(state)
        assert "risk_debate_state" in result
        assert result["risk_debate_state"]["count"] == 1
        assert result["risk_debate_state"]["latest_speaker"] == "Risky"

    def test_risk_manager_execution(self):
        """Test executing risk manager without LLM."""
        node = create_risk_manager(llm=None)
        state = {
            "trader_investment_plan": "建议买入",
            "risk_debate_state": {
                "history": "辩论历史",
                "count": 3,
            },
        }
        result = node(state)
        assert "risk_debate_state" in result
        assert "final_trade_decision" in result
        assert "风险" in result["final_trade_decision"]
