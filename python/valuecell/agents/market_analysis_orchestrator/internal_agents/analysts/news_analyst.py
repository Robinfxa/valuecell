"""News Analyst - News and current events analysis agent.

Analyzes news, announcements, and current events affecting the stock.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from .base import create_analyst_node, get_company_name, get_currency_info

NEWS_ANALYST_PROMPT = """你是一位专业的新闻分析师。

📋 **分析对象：**
- 公司名称：{company_name}
- 股票代码：{ticker}
- 所属市场：{market_type}
- 分析日期：{trade_date}

请提供以下新闻分析：

## 公司新闻
- 最新公告和公告
- 业绩预告/快报
- 重大事项披露
- 管理层变动

## 行业新闻
- 行业政策变化
- 行业竞争动态
- 供应链变化

## 宏观环境
- 宏观经济政策
- 利率/汇率变化
- 国际贸易动态

## 新闻情绪判断
- 整体新闻情绪：正面/中性/负面
- 对股价影响评估
- 关注的风险点

## 新闻面投资建议
- 基于新闻的短期影响判断
- 需要关注的后续事件

请使用中文回答。
"""


def create_news_analyst(llm: Any = None) -> Callable:
    """Create news analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    return create_analyst_node(
        analyst_type="news",
        prompt_template=NEWS_ANALYST_PROMPT,
        llm=llm,
        report_key="news_report",
    )
