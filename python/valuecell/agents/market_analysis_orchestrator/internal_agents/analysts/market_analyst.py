"""Market Analyst - Technical analysis agent.

Analyzes stock price trends, technical indicators, and market patterns.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from .base import create_analyst_node, get_company_name, get_currency_info

MARKET_ANALYST_PROMPT = """你是一位专业的股票技术分析师。

📋 **分析对象：**
- 公司名称：{company_name}
- 股票代码：{ticker}
- 所属市场：{market_type}
- 分析日期：{trade_date}
- 计价货币：{currency_name}（{currency_symbol}）

请基于技术分析方法，提供以下分析：

## 技术指标分析
- 移动平均线（MA5/10/20/60）走势
- MACD 指标分析
- RSI 相对强弱指标
- 布林带分析

## 价格趋势分析
- 短期趋势（5-10个交易日）
- 中期趋势（20-60个交易日）
- 关键支撑位和阻力位

## 成交量分析
- 量价配合情况
- 异常成交量信号

## 技术面投资建议
- 明确给出：买入/持有/卖出
- 目标价位区间
- 止损位建议

请使用中文回答。
"""


def create_market_analyst(llm: Any = None) -> Callable:
    """Create market analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    return create_analyst_node(
        analyst_type="market",
        prompt_template=MARKET_ANALYST_PROMPT,
        llm=llm,
        report_key="market_report",
    )


def create_market_analyst_standalone(llm: Any = None) -> Callable:
    """Create standalone market analyst for direct use.

    This version doesn't depend on state structure and can be
    called directly with ticker and date.

    Args:
        llm: Language model instance

    Returns:
        Callable that takes ticker and date, returns analysis
    """

    async def analyze(
        ticker: str,
        trade_date: str,
        market_type: str = "china",
    ) -> str:
        company_name = get_company_name(ticker, market_type)
        currency_info = get_currency_info(market_type)

        prompt = MARKET_ANALYST_PROMPT.format(
            ticker=ticker,
            company_name=company_name,
            trade_date=trade_date,
            market_type=market_type,
            currency_name=currency_info["currency_name"],
            currency_symbol=currency_info["currency_symbol"],
        )

        if llm is not None:
            response = await llm.ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        else:
            return f"市场技术分析: {company_name} ({ticker}) 当前处于技术位分析中"

    return analyze
