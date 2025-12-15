"""Base analyst functionality shared across all analysts.

This module provides common utilities and abstract patterns for
creating analyst nodes in the LangGraph workflow.
"""

from typing import Any, Callable, Dict, Optional

from loguru import logger


# ===== Template Manager Singleton =====

_template_manager = None


def get_template_manager():
    """Get the singleton TemplateManager instance."""
    global _template_manager
    if _template_manager is None:
        from ...prompts import TemplateManager
        _template_manager = TemplateManager()
    return _template_manager


def get_prompt_template(agent_type: str) -> str:
    """Get prompt template content from TemplateManager.
    
    Args:
        agent_type: Type of agent (from AgentType constants)
        
    Returns:
        Template content string, or empty string if not found
    """
    tm = get_template_manager()
    template = tm.get_default_template(agent_type)
    if template:
        logger.debug(f"Loaded template for {agent_type}: {template.name}")
        return template.content
    logger.warning(f"No template found for {agent_type}, using empty")
    return ""


def reload_templates() -> None:
    """Force reload templates (e.g., after editing via API)."""
    global _template_manager
    _template_manager = None
    logger.info("Template manager reset, will reload on next access")


def get_company_name(ticker: str, market_type: str) -> str:
    """Get company name from ticker symbol.

    Args:
        ticker: Stock ticker symbol
        market_type: Market type (china/hk/us)

    Returns:
        Company name or fallback
    """
    # US stock name mappings
    us_stock_names = {
        "AAPL": "苹果公司",
        "TSLA": "特斯拉",
        "NVDA": "英伟达",
        "MSFT": "微软",
        "GOOGL": "谷歌",
        "AMZN": "亚马逊",
        "META": "Meta",
        "NFLX": "奈飞",
        "BABA": "阿里巴巴",
        "JD": "京东",
    }

    if market_type == "us":
        return us_stock_names.get(ticker.upper(), f"美股{ticker}")
    elif market_type == "hk":
        clean_ticker = ticker.replace(".HK", "").replace(".hk", "")
        return f"港股{clean_ticker}"
    elif market_type == "china":
        # For China stocks, return a generic name
        # Full integration would call actual data source
        return f"股票{ticker}"
    else:
        return f"股票{ticker}"


def get_currency_info(market_type: str) -> Dict[str, str]:
    """Get currency information for market.

    Args:
        market_type: Market type (china/hk/us)

    Returns:
        Dict with currency_name and currency_symbol
    """
    currencies = {
        "china": {"currency_name": "人民币", "currency_symbol": "¥"},
        "hk": {"currency_name": "港币", "currency_symbol": "HK$"},
        "us": {"currency_name": "美元", "currency_symbol": "$"},
    }
    return currencies.get(market_type, currencies["china"])


def create_analyst_node(
    analyst_type: str,
    prompt_template: str,
    llm: Any,
    report_key: str,
) -> Callable:
    """Factory for creating analyst node functions.

    Args:
        analyst_type: Type of analyst (market/fundamentals/news/social)
        prompt_template: Prompt template string
        llm: Language model instance
        report_key: State key to store report

    Returns:
        Node function for LangGraph
    """

    def analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"📊 [{analyst_type}分析师] 开始分析")

        ticker = state.get("company_of_interest", "UNKNOWN")
        trade_date = state.get("trade_date", "")
        market_type = state.get("market_type", "china")

        company_name = get_company_name(ticker, market_type)
        currency_info = get_currency_info(market_type)

        prompt = prompt_template.format(
            ticker=ticker,
            company_name=company_name,
            trade_date=trade_date,
            market_type=market_type,
            currency_name=currency_info["currency_name"],
            currency_symbol=currency_info["currency_symbol"],
        )

        try:
            if llm is not None:
                response = llm.invoke(prompt)
                report = response.content if hasattr(response, "content") else str(response)
            else:
                # Placeholder when no LLM
                report = f"{analyst_type}分析: {company_name} ({ticker}) 分析报告占位符"
        except Exception as e:
            logger.exception(f"❌ [{analyst_type}分析师] 分析失败: {e}")
            report = f"{analyst_type}分析失败: {e}"

        logger.info(f"✅ [{analyst_type}分析师] 完成，报告长度: {len(report)}")

        # Update tool call counter
        counter_key = f"{analyst_type}_tool_call_count"

        return {
            report_key: report,
            counter_key: state.get(counter_key, 0) + 1,
        }

    return analyst_node
