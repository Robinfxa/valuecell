"""Fundamentals Analyst - Financial fundamentals analysis agent.

Analyzes company financials, valuations, and business fundamentals.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from .base import create_analyst_node, get_company_name, get_currency_info

FUNDAMENTALS_ANALYST_PROMPT = """你是一位专业的基本面分析师。

📋 **分析对象：**
- 公司名称：{company_name}
- 股票代码：{ticker}
- 所属市场：{market_type}
- 分析日期：{trade_date}
- 计价货币：{currency_name}（{currency_symbol}）

请提供以下基本面分析：

## 财务状况分析
- 收入和利润趋势
- 毛利率和净利率
- 现金流状况
- 资产负债率

## 估值分析
- PE（市盈率）分析
- PB（市净率）分析
- PS（市销率）分析
- 与行业平均对比

## 成长性分析
- 收入增长率
- 利润增长率
- 未来增长预期

## 竞争优势分析
- 行业地位
- 护城河
- 管理层质量

## 基本面投资建议
- 明确给出：买入/持有/卖出
- 合理估值区间
- 风险因素

请使用中文回答。
"""


def create_fundamentals_analyst(llm: Any = None) -> Callable:
    """Create fundamentals analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    return create_analyst_node(
        analyst_type="fundamentals",
        prompt_template=FUNDAMENTALS_ANALYST_PROMPT,
        llm=llm,
        report_key="fundamentals_report",
    )
