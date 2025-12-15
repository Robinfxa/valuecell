"""Bear Researcher - Bearish argument agent.

Builds the case for caution/selling based on risk factors.
Uses TemplateManager for dynamic prompt loading.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..analysts.base import get_prompt_template, get_company_name, get_currency_info
from ...prompts import AgentType


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

        # Get company name and currency info
        from ..analysts.base import get_company_name, get_currency_info

        company_name = get_company_name(ticker, market_type)
        currency_info = get_currency_info(market_type)

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
        
        # Get past memories (if available)
        past_memories = state.get("past_memories", "暂无历史记忆")

        # Load template dynamically
        template_content = get_prompt_template(AgentType.BEAR_RESEARCHER)
        
        prompt = template_content.format(
            company_name=company_name,
            ticker=ticker,
            market_type=market_type,
            currency_name=currency_info["currency_name"],
            currency_symbol=currency_info["currency_symbol"],
            market_report=market_report or "暂无",
            sentiment_report=sentiment_report or "暂无",
            news_report=news_report or "暂无",
            fundamentals_report=fundamentals_report or "暂无",
            debate_history=debate_history or "无历史",
            bull_response=bull_response or "无看涨论点",
            past_memories=past_memories,
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                argument = response.content if hasattr(response, "content") else str(response)
            else:
                argument = f"看跌论点: {company_name} 存在估值过高和增长不确定性风险，建议谨慎"
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
