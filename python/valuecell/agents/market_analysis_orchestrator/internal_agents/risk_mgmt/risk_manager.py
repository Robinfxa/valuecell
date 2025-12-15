"""Risk Manager - Final risk decision maker.

Summarizes risk debate and makes final risk assessment.
Uses TemplateManager for dynamic prompt loading.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..analysts.base import get_prompt_template
from ...prompts import AgentType


def create_risk_manager(llm: Any = None) -> Callable:
    """Create risk manager node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """

    def risk_manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("👔 [风险经理] 开始最终评估")

        trader_decision = state.get("trader_investment_plan", "")

        # Get risk debate state
        risk_state = state.get("risk_debate_state") or {}
        risk_history = risk_state.get("history", "")
        risky_response = risk_state.get("current_risky_response", "")
        safe_response = risk_state.get("current_safe_response", "")
        neutral_response = risk_state.get("current_neutral_response", "")

        # Load template dynamically
        template_content = get_prompt_template(AgentType.RISK_MANAGER)
        
        prompt = template_content.format(
            trader_decision=trader_decision or "待评估",
            risk_history=risk_history or "无辩论历史",
            risky_response=risky_response or "暂无",
            safe_response=safe_response or "暂无",
            neutral_response=neutral_response or "暂无",
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                decision = response.content if hasattr(response, "content") else str(response)
            else:
                decision = "风险评估: 综合分析后，风险等级为中等，建议控制仓位在30%以内，设置5%止损"
        except Exception as e:
            logger.exception(f"❌ [风险经理] 决策失败: {e}")
            decision = f"风险评估失败: {e}"

        # Update risk debate state with final decision
        new_risk_state = {
            "judge_decision": decision,
            "history": risk_state.get("history", ""),
            "risky_history": risk_state.get("risky_history", ""),
            "safe_history": risk_state.get("safe_history", ""),
            "neutral_history": risk_state.get("neutral_history", ""),
            "latest_speaker": "Risk Manager",
            "current_risky_response": risk_state.get("current_risky_response", ""),
            "current_safe_response": risk_state.get("current_safe_response", ""),
            "current_neutral_response": risk_state.get("current_neutral_response", ""),
            "count": risk_state.get("count", 0),
        }

        logger.info(f"✅ [风险经理] 完成，决策长度: {len(decision)}")

        return {
            "risk_debate_state": new_risk_state,
            "final_trade_decision": decision,
        }

    return risk_manager_node
