"""Aggressive Risk Debater - High-risk tolerance advocate.

Advocates for aggressive risk-taking to maximize returns.
Uses TemplateManager for dynamic prompt loading.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..analysts.base import get_prompt_template
from ...prompts import AgentType


def create_risky_debater(llm: Any = None) -> Callable:
    """Create aggressive risk debater node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def risky_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("🔥 [激进风险分析师] 开始论证")

        # Get reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        trader_decision = state.get("trader_investment_plan", "")

        # Get risk debate state
        risk_state = state.get("risk_debate_state") or {}
        risk_history = risk_state.get("history", "")
        risky_history = risk_state.get("risky_history", "")
        safe_response = risk_state.get("current_safe_response", "")
        neutral_response = risk_state.get("current_neutral_response", "")

        # Load template dynamically
        template_content = get_prompt_template(AgentType.RISKY_DEBATER)
        
        prompt = template_content.format(
            trader_decision=trader_decision or "待评估",
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            risk_history=risk_history or "无历史",
            safe_response=safe_response or "暂无",
            neutral_response=neutral_response or "暂无",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = "激进观点: 当前市场机会大于风险，建议积极建仓，把握上涨行情"
        except Exception as e:
            logger.exception(f"❌ [激进风险分析师] 生成失败: {e}")
            argument = f"激进分析失败: {e}"

        full_argument = f"Risky Analyst: {argument}"

        # Update risk debate state
        new_risk_state = {
            "history": risk_history + "\n" + full_argument,
            "risky_history": risky_history + "\n" + full_argument,
            "safe_history": risk_state.get("safe_history", ""),
            "neutral_history": risk_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": full_argument,
            "current_safe_response": risk_state.get("current_safe_response", ""),
            "current_neutral_response": risk_state.get("current_neutral_response", ""),
            "count": risk_state.get("count", 0) + 1,
        }

        logger.info(f"✅ [激进风险分析师] 完成，论点长度: {len(argument)}")

        return {"risk_debate_state": new_risk_state}

    return risky_node
