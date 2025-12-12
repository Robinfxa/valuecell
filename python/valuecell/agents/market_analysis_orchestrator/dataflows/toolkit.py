"""Toolkit for creating LangChain-compatible tools.

Provides a collection of tools that internal agents can use
to fetch market data, news, and other information.
"""

from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from .data_tools import (
    get_social_sentiment,
    get_stock_fundamentals,
    get_stock_market_data,
    get_stock_news,
)


class DataToolkit:
    """Collection of data fetching tools for agents.

    This toolkit provides methods that can be bound to LLM agents
    for fetching market data, fundamentals, news, and sentiment.
    """

    def __init__(self, market_type: str = "china"):
        """Initialize toolkit.

        Args:
            market_type: Default market type for data queries
        """
        self.market_type = market_type
        logger.info("DataToolkit initialized", market_type=market_type)

    def get_stock_market_data_unified(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> str:
        """Unified market data tool.

        Automatically detects stock type (A-shares/HK/US) and
        fetches data from appropriate source.

        Args:
            ticker: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Formatted market data string
        """
        # Detect market type from ticker
        market_type = self._detect_market_type(ticker)
        return get_stock_market_data(ticker, start_date, end_date, market_type)

    def get_stock_fundamentals_unified(self, ticker: str) -> str:
        """Unified fundamentals tool.

        Args:
            ticker: Stock ticker

        Returns:
            Formatted fundamentals string
        """
        market_type = self._detect_market_type(ticker)
        return get_stock_fundamentals(ticker, market_type)

    def get_stock_news_unified(
        self,
        ticker: str,
        days: int = 7,
    ) -> str:
        """Unified news tool.

        Args:
            ticker: Stock ticker
            days: Days to look back

        Returns:
            Formatted news string
        """
        market_type = self._detect_market_type(ticker)
        return get_stock_news(ticker, days, market_type)

    def get_social_sentiment_unified(self, ticker: str) -> str:
        """Unified sentiment tool.

        Args:
            ticker: Stock ticker

        Returns:
            Formatted sentiment string
        """
        market_type = self._detect_market_type(ticker)
        return get_social_sentiment(ticker, market_type)

    def _detect_market_type(self, ticker: str) -> str:
        """Detect market type from ticker format.

        Args:
            ticker: Stock ticker

        Returns:
            Market type string (china/hk/us)
        """
        ticker_upper = ticker.upper()

        # China A-shares: 000001.SZ, 600036.SH
        if ticker_upper.endswith(".SZ") or ticker_upper.endswith(".SH"):
            return "china"
        if ticker_upper.startswith("SZSE:") or ticker_upper.startswith("SSE:"):
            return "china"

        # Hong Kong: 0700.HK
        if ticker_upper.endswith(".HK"):
            return "hk"
        if ticker_upper.startswith("HKEX:"):
            return "hk"

        # US stocks: AAPL, GOOGL
        if ticker.isalpha() and len(ticker) <= 5:
            return "us"
        if ticker_upper.startswith("NASDAQ:") or ticker_upper.startswith("NYSE:"):
            return "us"

        # Default
        return self.market_type

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools with metadata.

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "get_stock_market_data_unified",
                "description": "获取股票市场数据（价格、成交量、技术指标）",
                "function": self.get_stock_market_data_unified,
            },
            {
                "name": "get_stock_fundamentals_unified",
                "description": "获取股票基本面数据（财务指标、估值）",
                "function": self.get_stock_fundamentals_unified,
            },
            {
                "name": "get_stock_news_unified",
                "description": "获取股票相关新闻",
                "function": self.get_stock_news_unified,
            },
            {
                "name": "get_social_sentiment_unified",
                "description": "获取社交媒体情绪分析",
                "function": self.get_social_sentiment_unified,
            },
        ]


def create_toolkit(market_type: str = "china") -> DataToolkit:
    """Create a data toolkit instance.

    Args:
        market_type: Default market type

    Returns:
        DataToolkit instance
    """
    return DataToolkit(market_type=market_type)
