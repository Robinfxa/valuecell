"""Conservative Risk Debater - Risk-averse advocate.

Advocates for capital preservation and cautious approach.
Uses TemplateManager for dynamic prompt loading.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..analysts.base import get_prompt_template
from ...prompts import AgentType


def create_safe_debater(llm: Any = None) -> Callable:
    """Create conservative risk debater node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def safe_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("🛡️ [保守风险分析师] 开始论证")

        # Get reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        trader_decision = state.get("trader_investment_plan", "")

        # Get risk debate state
        risk_state = state.get("risk_debate_state") or {}
        risk_history = risk_state.get("history", "")
        safe_history = risk_state.get("safe_history", "")
        risky_response = risk_state.get("current_risky_response", "")
        neutral_response = risk_state.get("current_neutral_response", "")

        # Load template dynamically
        template_content = get_prompt_template(AgentType.SAFE_DEBATER)
        
        prompt = template_content.format(
            trader_decision=trader_decision or "待评估",
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            risk_history=risk_history or "无历史",
            risky_response=risky_response or "暂无",
            neutral_response=neutral_response or "暂无",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = "保守观点: 当前市场不确定性较高，建议控制仓位，设置止损，保护本金"
        except Exception as e:
            logger.exception(f"❌ [保守风险分析师] 生成失败: {e}")
            argument = f"保守分析失败: {e}"

        full_argument = f"Safe Analyst: {argument}"

        # Update risk debate state
        new_risk_state = {
            "history": risk_history + "\n" + full_argument,
            "risky_history": risk_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + full_argument,
            "neutral_history": risk_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_state.get("current_risky_response", ""),
            "current_safe_response": full_argument,
            "current_neutral_response": risk_state.get("current_neutral_response", ""),
            "count": risk_state.get("count", 0) + 1,
        }

        logger.info(f"✅ [保守风险分析师] 完成，论点长度: {len(argument)}")

        return {"risk_debate_state": new_risk_state}

    return safe_node
