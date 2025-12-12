"""Research Manager - Debate moderator and decision maker.

Summarizes the bull/bear debate and makes investment recommendation.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

RESEARCH_MANAGER_PROMPT = """作为投资组合经理和辩论主持人，你的职责是批判性地评估这轮辩论并做出明确决策。

## 综合分析报告
市场研究：{market_report}
情绪分析：{sentiment_report}
新闻分析：{news_report}
基本面分析：{fundamentals_report}

## 辩论历史
{debate_history}

## 你的任务
1. 简洁地总结双方的关键观点
2. 做出明确决策：买入、卖出或持有
3. 提供投资计划，包括：
   - 建议理由
   - 战略行动
   - 目标价格区间
   - 风险提示

请用中文以对话方式撰写分析，避免使用特殊格式。
"""


def create_research_manager(llm: Any = None) -> Callable:
    """Create research manager node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def research_manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("👔 [研究经理] 开始总结辩论")

        # Get reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")

        # Get debate state
        invest_state = state.get("investment_debate_state") or {}
        debate_history = invest_state.get("history", "")

        prompt = RESEARCH_MANAGER_PROMPT.format(
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            debate_history=debate_history or "无辩论历史",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                decision = response.content if hasattr(response, "content") else str(response)
            else:
                decision = "综合分析：基于多空双方论点，建议持有观望，等待更明确的信号"
        except Exception as e:
            logger.exception(f"❌ [研究经理] 决策失败: {e}")
            decision = f"研究决策失败: {e}"

        # Update debate state with judge decision
        new_invest_state = {
            "judge_decision": decision,
            "history": invest_state.get("history", ""),
            "bear_history": invest_state.get("bear_history", ""),
            "bull_history": invest_state.get("bull_history", ""),
            "current_response": decision,
            "count": invest_state.get("count", 0),
        }

        logger.info(f"✅ [研究经理] 完成，决策长度: {len(decision)}")

        return {
            "investment_debate_state": new_invest_state,
            "investment_plan": decision,
        }

    return research_manager_node
