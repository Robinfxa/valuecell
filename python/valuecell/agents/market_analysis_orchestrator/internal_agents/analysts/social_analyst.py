"""Social Media Analyst - Sentiment analysis agent.

Analyzes social media sentiment and market psychology.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from .base import create_analyst_node, get_company_name, get_currency_info

SOCIAL_ANALYST_PROMPT = """你是一位专业的社交媒体情绪分析师。

📋 **分析对象：**
- 公司名称：{company_name}
- 股票代码：{ticker}
- 所属市场：{market_type}
- 分析日期：{trade_date}

请提供以下社交媒体情绪分析：

## 社交媒体热度
- 讨论热度变化
- 主要讨论话题
- 意见领袖观点

## 投资者情绪
- 散户情绪指标
- 机构观点汇总
- 市场预期变化

## 情绪指标
- 恐惧与贪婪指数
- 看多/看空比例
- 情绪极端信号

## 舆情风险
- 负面舆情监控
- 潜在舆情风险
- 舆情应对建议

## 情绪面投资建议
- 当前情绪阶段判断
- 逆向投资机会
- 需要警惕的情绪陷阱

请使用中文回答。
"""


def create_social_analyst(llm: Any = None) -> Callable:
    """Create social media analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    return create_analyst_node(
        analyst_type="sentiment",
        prompt_template=SOCIAL_ANALYST_PROMPT,
        llm=llm,
        report_key="sentiment_report",
    )
