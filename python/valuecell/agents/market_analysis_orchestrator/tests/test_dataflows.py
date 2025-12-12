"""Tests for dataflows module."""

import pytest

from valuecell.agents.market_analysis_orchestrator.dataflows import (
    DataToolkit,
    create_toolkit,
    get_social_sentiment,
    get_stock_fundamentals,
    get_stock_market_data,
    get_stock_news,
)
from valuecell.agents.market_analysis_orchestrator.dataflows.data_tools import (
    convert_ticker_to_internal,
)


class TestTickerConversion:
    """Tests for ticker format conversion."""

    def test_china_sz_ticker(self):
        """Test China SZ ticker conversion."""
        result = convert_ticker_to_internal("000001.SZ", "china")
        assert result == "SZSE:000001"

    def test_china_sh_ticker(self):
        """Test China SH ticker conversion."""
        result = convert_ticker_to_internal("600036.SH", "china")
        assert result == "SSE:600036"

    def test_hk_ticker(self):
        """Test HK ticker conversion."""
        result = convert_ticker_to_internal("0700.HK", "hk")
        assert result == "HKEX:0700"

    def test_us_ticker(self):
        """Test US ticker conversion."""
        result = convert_ticker_to_internal("AAPL", "us")
        assert result == "NASDAQ:AAPL"

    def test_already_internal(self):
        """Test already internal format."""
        result = convert_ticker_to_internal("SZSE:000001", "china")
        assert result == "SZSE:000001"


class TestDataTools:
    """Tests for data tool functions."""

    def test_get_stock_market_data_mock(self):
        """Test getting mock market data."""
        result = get_stock_market_data("000001.SZ", "2025-12-01", "2025-12-12", "china")
        assert "市场数据" in result
        assert "000001.SZ" in result

    def test_get_stock_fundamentals_mock(self):
        """Test getting mock fundamentals."""
        result = get_stock_fundamentals("AAPL", "us")
        assert "基本面" in result
        assert "AAPL" in result

    def test_get_stock_news(self):
        """Test getting news."""
        result = get_stock_news("TSLA", 7, "us")
        assert "新闻" in result

    def test_get_social_sentiment(self):
        """Test getting sentiment."""
        result = get_social_sentiment("NVDA", "us")
        assert "情绪" in result


class TestDataToolkit:
    """Tests for DataToolkit."""

    @pytest.fixture
    def toolkit(self):
        return create_toolkit("china")

    def test_create_toolkit(self, toolkit):
        """Test toolkit creation."""
        assert isinstance(toolkit, DataToolkit)
        assert toolkit.market_type == "china"

    def test_get_all_tools(self, toolkit):
        """Test getting all tools."""
        tools = toolkit.get_all_tools()
        assert len(tools) == 4
        assert all("name" in t for t in tools)
        assert all("function" in t for t in tools)

    def test_detect_market_type_china(self, toolkit):
        """Test detecting China market."""
        assert toolkit._detect_market_type("000001.SZ") == "china"
        assert toolkit._detect_market_type("600036.SH") == "china"

    def test_detect_market_type_hk(self, toolkit):
        """Test detecting HK market."""
        assert toolkit._detect_market_type("0700.HK") == "hk"

    def test_detect_market_type_us(self, toolkit):
        """Test detecting US market."""
        assert toolkit._detect_market_type("AAPL") == "us"
        assert toolkit._detect_market_type("GOOGL") == "us"

    def test_unified_market_data(self, toolkit):
        """Test unified market data tool."""
        result = toolkit.get_stock_market_data_unified(
            "000001.SZ", "2025-12-01", "2025-12-12"
        )
        assert "市场数据" in result

    def test_unified_fundamentals(self, toolkit):
        """Test unified fundamentals tool."""
        result = toolkit.get_stock_fundamentals_unified("AAPL")
        assert "基本面" in result
