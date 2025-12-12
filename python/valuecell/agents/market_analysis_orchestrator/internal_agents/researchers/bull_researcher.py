"""Bull Researcher - Bullish argument agent.

Builds the case for buying/holding based on positive indicators.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

BULL_RESEARCHER_PROMPT = """你是一位看涨分析师，负责为股票 {company_name}（{ticker}）的投资建立强有力的论证。

## 你的任务
构建基于证据的强有力案例，强调增长潜力、竞争优势和积极的市场指标。

## 可用信息
市场研究报告：{market_report}
社交媒体情绪报告：{sentiment_report}
新闻报告：{news_report}
基本面报告：{fundamentals_report}

辩论历史：{debate_history}
最后的看跌论点：{bear_response}

## 请重点关注
- 增长潜力：突出公司的市场机会、收入预测和可扩展性
- 竞争优势：强调独特产品、强势品牌或主导市场地位
- 积极指标：使用财务健康状况、行业趋势和最新积极消息作为证据
- 反驳看跌观点：用具体数据和合理推理批判性分析看跌论点

请使用中文回答，以对话风格呈现你的论点。
"""


def create_bull_researcher(llm: Any = None) -> Callable:
    """Create bull researcher node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def bull_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("🐂 [看涨研究员] 开始论证")

        ticker = state.get("company_of_interest", "UNKNOWN")
        market_type = state.get("market_type", "china")

        # Get company name
        from ..analysts.base import get_company_name

        company_name = get_company_name(ticker, market_type)

        # Get reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")

        # Get debate state
        invest_state = state.get("investment_debate_state") or {}
        debate_history = invest_state.get("history", "")
        bear_response = invest_state.get("current_response", "")
        bull_history = invest_state.get("bull_history", "")

        prompt = BULL_RESEARCHER_PROMPT.format(
            company_name=company_name,
            ticker=ticker,
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            debate_history=debate_history or "无历史",
            bear_response=bear_response or "无看跌论点",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = f"看涨论点: {company_name} 具有良好的增长潜力和竞争优势，建议买入"
        except Exception as e:
            logger.exception(f"❌ [看涨研究员] 生成失败: {e}")
            argument = f"看涨分析失败: {e}"

        full_argument = f"Bull Analyst: {argument}"

        # Update debate state
        new_invest_state = {
            "history": debate_history + "\n" + full_argument,
            "bull_history": bull_history + "\n" + full_argument,
            "bear_history": invest_state.get("bear_history", ""),
            "current_response": full_argument,
            "count": invest_state.get("count", 0) + 1,
        }

        logger.info(f"✅ [看涨研究员] 完成，论点长度: {len(argument)}")

        return {"investment_debate_state": new_invest_state}

    return bull_node
