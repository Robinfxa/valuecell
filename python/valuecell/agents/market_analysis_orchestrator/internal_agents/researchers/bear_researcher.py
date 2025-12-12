"""Bear Researcher - Bearish argument agent.

Builds the case for selling/avoiding based on risk factors.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

BEAR_RESEARCHER_PROMPT = """你是一位看跌分析师，负责为股票 {company_name}（{ticker}）提出谨慎的论证。

## 你的任务
构建基于证据的论点，强调风险因素、估值担忧和潜在问题。

## 可用信息
市场研究报告：{market_report}
社交媒体情绪报告：{sentiment_report}
新闻报告：{news_report}
基本面报告：{fundamentals_report}

辩论历史：{debate_history}
最后的看涨论点：{bull_response}

## 请重点关注
- 风险因素：突出公司面临的挑战和不确定性
- 估值问题：分析当前估值是否合理
- 竞争威胁：指出竞争对手和市场变化的影响
- 反驳看涨观点：用具体数据质疑过于乐观的假设

请使用中文回答，以对话风格呈现你的论点。
"""


def create_bear_researcher(llm: Any = None) -> Callable:
    """Create bear researcher node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def bear_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("🐻 [看跌研究员] 开始论证")

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
        bull_response = invest_state.get("current_response", "")
        bear_history = invest_state.get("bear_history", "")

        prompt = BEAR_RESEARCHER_PROMPT.format(
            company_name=company_name,
            ticker=ticker,
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            debate_history=debate_history or "无历史",
            bull_response=bull_response or "无看涨论点",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = f"看跌论点: {company_name} 存在估值过高和市场风险，建议谨慎"
        except Exception as e:
            logger.exception(f"❌ [看跌研究员] 生成失败: {e}")
            argument = f"看跌分析失败: {e}"

        full_argument = f"Bear Analyst: {argument}"

        # Update debate state
        new_invest_state = {
            "history": debate_history + "\n" + full_argument,
            "bull_history": invest_state.get("bull_history", ""),
            "bear_history": bear_history + "\n" + full_argument,
            "current_response": full_argument,
            "count": invest_state.get("count", 0) + 1,
        }

        logger.info(f"✅ [看跌研究员] 完成，论点长度: {len(argument)}")

        return {"investment_debate_state": new_invest_state}

    return bear_node
