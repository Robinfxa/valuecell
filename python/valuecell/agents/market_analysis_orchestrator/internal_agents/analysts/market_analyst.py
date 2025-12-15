"""Market Analyst - Loads prompt from TemplateManager.

Analyzes technical indicators and price trends.
"""

from typing import Any, Callable

from loguru import logger

from .base import create_analyst_node, get_prompt_template
from ...prompts import AgentType


def create_market_analyst(llm: Any = None) -> Callable:
    """Create market analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    # Load template dynamically from TemplateManager
    prompt_template = get_prompt_template(AgentType.MARKET_ANALYST)
    
    return create_analyst_node(
        analyst_type="market",
        prompt_template=prompt_template,
        llm=llm,
        report_key="market_report",
    )
