"""Social Analyst - Loads prompt from TemplateManager.

Analyzes social media sentiment and investor mood.
"""

from typing import Any, Callable

from loguru import logger

from .base import create_analyst_node, get_prompt_template
from ...prompts import AgentType


def create_social_analyst(llm: Any = None) -> Callable:
    """Create social analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    # Load template dynamically from TemplateManager
    prompt_template = get_prompt_template(AgentType.SOCIAL_ANALYST)
    
    return create_analyst_node(
        analyst_type="social",
        prompt_template=prompt_template,
        llm=llm,
        report_key="sentiment_report",
    )
