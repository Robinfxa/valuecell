"""News Analyst - Loads prompt from TemplateManager.

Analyzes news and current events impact on stock.
"""

from typing import Any, Callable

from loguru import logger

from .base import create_analyst_node, get_prompt_template
from ...prompts import AgentType


def create_news_analyst(llm: Any = None) -> Callable:
    """Create news analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    # Load template dynamically from TemplateManager
    prompt_template = get_prompt_template(AgentType.NEWS_ANALYST)
    
    return create_analyst_node(
        analyst_type="news",
        prompt_template=prompt_template,
        llm=llm,
        report_key="news_report",
    )
