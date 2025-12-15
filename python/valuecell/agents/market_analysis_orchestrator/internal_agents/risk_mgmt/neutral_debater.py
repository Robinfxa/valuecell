"""Neutral Risk Debater - Balanced perspective advocate.

Provides balanced view considering both risks and opportunities.
Uses TemplateManager for dynamic prompt loading.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..analysts.base import get_prompt_template
from ...prompts import AgentType


def create_neutral_debater(llm: Any = None) -> Callable:
    """Create neutral risk debater node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def neutral_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("⚖️ [中性风险分析师] 开始论证")

        # Get reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        trader_decision = state.get("trader_investment_plan", "")

        # Get risk debate state
        risk_state = state.get("risk_debate_state") or {}
        risk_history = risk_state.get("history", "")
        neutral_history = risk_state.get("neutral_history", "")
        risky_response = risk_state.get("current_risky_response", "")
        safe_response = risk_state.get("current_safe_response", "")

        # Load template dynamically
        template_content = get_prompt_template(AgentType.NEUTRAL_DEBATER)
        
        prompt = template_content.format(
            trader_decision=trader_decision or "待评估",
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            risk_history=risk_history or "无历史",
            risky_response=risky_response or "暂无",
            safe_response=safe_response or "暂无",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = "中性观点: 建议采取平衡策略，小仓位试探，根据市场反馈逐步调整"
        except Exception as e:
            logger.exception(f"❌ [中性风险分析师] 生成失败: {e}")
            argument = f"中性分析失败: {e}"

        full_argument = f"Neutral Analyst: {argument}"

        # Update risk debate state
        new_risk_state = {
            "history": risk_history + "\n" + full_argument,
            "risky_history": risk_state.get("risky_history", ""),
            "safe_history": risk_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + full_argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_state.get("current_risky_response", ""),
            "current_safe_response": risk_state.get("current_safe_response", ""),
            "current_neutral_response": full_argument,
            "count": risk_state.get("count", 0) + 1,
        }

        logger.info(f"✅ [中性风险分析师] 完成，论点长度: {len(argument)}")

        return {"risk_debate_state": new_risk_state}

    return neutral_node
