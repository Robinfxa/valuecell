"""Data tools for market analysis agents.

This module provides LangChain-compatible tools that wrap ValueCell's
AdapterManager for use by the internal analyst agents.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger


def get_adapter_manager():
    """Get the AdapterManager singleton.

    Returns:
        AdapterManager instance
    """
    try:
        from valuecell.adapters.assets import AdapterManager

        manager = AdapterManager()

        # Configure available adapters
        try:
            manager.configure_akshare()
        except Exception as e:
            logger.debug(f"AKShare adapter not configured: {e}")

        try:
            manager.configure_yfinance()
        except Exception as e:
            logger.debug(f"YFinance adapter not configured: {e}")

        try:
            manager.configure_baostock()
        except Exception as e:
            logger.debug(f"BaoStock adapter not configured: {e}")

        return manager
    except ImportError:
        logger.warning("AdapterManager not available, using mock data")
        return None


def convert_ticker_to_internal(ticker: str, market_type: str) -> str:
    """Convert external ticker to internal format.

    Args:
        ticker: External ticker (e.g., "000001.SZ", "AAPL")
        market_type: Market type (china/hk/us)

    Returns:
        Internal ticker format (e.g., "SZSE:000001", "NASDAQ:AAPL")
    """
    if ":" in ticker:
        return ticker  # Already in internal format

    if market_type == "china":
        if ticker.endswith(".SZ"):
            return f"SZSE:{ticker.replace('.SZ', '')}"
        elif ticker.endswith(".SH"):
            return f"SSE:{ticker.replace('.SH', '')}"
        else:
            # Default to SZSE for 6-digit codes starting with 0/3
            code = ticker.split(".")[0]
            if code.startswith(("0", "3")):
                return f"SZSE:{code}"
            else:
                return f"SSE:{code}"
    elif market_type == "hk":
        code = ticker.replace(".HK", "").replace(".hk", "")
        return f"HKEX:{code}"
    elif market_type == "us":
        # US stocks - try to determine exchange
        return f"NASDAQ:{ticker}"
    else:
        return ticker


def get_stock_market_data(
    ticker: str,
    start_date: str,
    end_date: str,
    market_type: str = "china",
) -> str:
    """Get stock market data for analysis.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        market_type: Market type (china/hk/us)

    Returns:
        Formatted market data string
    """
    logger.info(
        f"📊 [DataTools] Getting market data",
        ticker=ticker,
        start=start_date,
        end=end_date,
    )

    manager = get_adapter_manager()

    if manager is None:
        return _get_mock_market_data(ticker, start_date, end_date)

    try:
        internal_ticker = convert_ticker_to_internal(ticker, market_type)

        # Get real-time price
        price = manager.get_real_time_price(internal_ticker)

        # Get historical prices
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Extend range for better analysis
        extended_start = start_dt - timedelta(days=30)
        historical = manager.get_historical_prices(
            internal_ticker, extended_start, end_dt
        )

        # Format output
        output = f"## {ticker} 市场数据\n\n"

        if price:
            output += f"### 实时行情\n"
            output += f"- 当前价格: {price.current}\n"
            output += f"- 今日涨跌: {price.change_percent:.2f}%\n" if price.change_percent else ""
            output += f"- 成交量: {price.volume:,}\n" if price.volume else ""
            output += f"- 最高: {price.high}\n" if price.high else ""
            output += f"- 最低: {price.low}\n" if price.low else ""
            output += "\n"

        if historical:
            output += f"### 历史数据 (最近{len(historical)}天)\n"
            for i, hp in enumerate(historical[-5:]):  # Last 5 days
                output += f"- {hp.timestamp.strftime('%Y-%m-%d')}: "
                output += f"开{hp.open:.2f} 高{hp.high:.2f} 低{hp.low:.2f} 收{hp.close:.2f}\n"

        return output

    except Exception as e:
        logger.exception(f"Error getting market data: {e}")
        return _get_mock_market_data(ticker, start_date, end_date)


def _get_mock_market_data(ticker: str, start_date: str, end_date: str) -> str:
    """Generate mock market data for testing."""
    return f"""## {ticker} 市场数据（模拟）

### 实时行情
- 当前价格: 25.50
- 今日涨跌: +1.25%
- 成交量: 1,234,567
- 最高: 25.80
- 最低: 25.10

### 历史数据 (最近5天)
- 2025-12-11: 开25.20 高25.60 低25.00 收25.50
- 2025-12-10: 开24.80 高25.30 低24.60 收25.20
- 2025-12-09: 开25.00 高25.20 低24.50 收24.80
- 2025-12-08: 开24.50 高25.10 低24.30 收25.00
- 2025-12-07: 开24.20 高24.80 低24.00 收24.50

### 技术指标
- MA5: 25.00
- MA10: 24.80
- MA20: 24.50
- RSI(14): 55.6
- MACD: 0.12
"""


def get_stock_fundamentals(ticker: str, market_type: str = "china") -> str:
    """Get stock fundamental data.

    Args:
        ticker: Stock ticker symbol
        market_type: Market type

    Returns:
        Formatted fundamentals string
    """
    logger.info(f"📊 [DataTools] Getting fundamentals", ticker=ticker)

    manager = get_adapter_manager()

    if manager is None:
        return _get_mock_fundamentals(ticker)

    try:
        internal_ticker = convert_ticker_to_internal(ticker, market_type)
        asset = manager.get_asset_info(internal_ticker)

        if not asset:
            return _get_mock_fundamentals(ticker)

        output = f"## {asset.name or ticker} 基本面数据\n\n"
        output += f"- 股票代码: {ticker}\n"
        output += f"- 公司名称: {asset.name}\n" if asset.name else ""
        output += f"- 所属行业: {asset.sector}\n" if asset.sector else ""
        output += f"- 市值: {asset.market_cap:,.0f}\n" if asset.market_cap else ""
        output += f"- 市盈率(PE): {asset.pe_ratio:.2f}\n" if asset.pe_ratio else ""
        output += f"- 市净率(PB): {asset.pb_ratio:.2f}\n" if asset.pb_ratio else ""

        return output

    except Exception as e:
        logger.exception(f"Error getting fundamentals: {e}")
        return _get_mock_fundamentals(ticker)


def _get_mock_fundamentals(ticker: str) -> str:
    """Generate mock fundamentals data."""
    return f"""## {ticker} 基本面数据（模拟）

- 股票代码: {ticker}
- 公司名称: 示例公司
- 所属行业: 科技
- 市值: 100,000,000,000
- 市盈率(PE): 25.5
- 市净率(PB): 3.2
- 每股收益(EPS): 2.50
- 净利润率: 15.2%
- 资产负债率: 45.0%
- ROE: 18.5%
"""


def get_stock_news(
    ticker: str,
    days: int = 7,
    market_type: str = "china",
) -> str:
    """Get recent news for a stock.

    Args:
        ticker: Stock ticker symbol
        days: Number of days to look back
        market_type: Market type

    Returns:
        Formatted news string
    """
    logger.info(f"📰 [DataTools] Getting news", ticker=ticker, days=days)

    # For now, return mock news
    # TODO: Integrate with news APIs
    return f"""## {ticker} 近期新闻

### 行业动态
- 行业政策保持稳定，监管环境向好
- 市场竞争加剧，头部企业优势明显

### 公司公告
- 暂无重大公告

### 市场评论
- 机构评级维持"买入"
- 分析师预期业绩稳健

**新闻情绪**: 中性偏正面
"""


def get_social_sentiment(ticker: str, market_type: str = "china") -> str:
    """Get social media sentiment for a stock.

    Args:
        ticker: Stock ticker symbol
        market_type: Market type

    Returns:
        Formatted sentiment string
    """
    logger.info(f"💬 [DataTools] Getting sentiment", ticker=ticker)

    # For now, return mock sentiment
    # TODO: Integrate with sentiment APIs
    return f"""## {ticker} 社交媒体情绪分析

### 讨论热度
- 讨论量: 中等
- 话题趋势: 平稳

### 投资者情绪
- 看多比例: 55%
- 看空比例: 25%
- 观望比例: 20%

### 关键词云
- 业绩、增长、稳健、分红

**综合情绪**: 偏乐观
"""
