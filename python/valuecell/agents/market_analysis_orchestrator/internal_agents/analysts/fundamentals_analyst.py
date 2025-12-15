"""Fundamentals Analyst - Loads prompt from TemplateManager.

Analyzes company fundamentals, financials, and valuation.
"""

from typing import Any, Callable

from loguru import logger

from .base import create_analyst_node, get_prompt_template
from ...prompts import AgentType


def create_fundamentals_analyst(llm: Any = None) -> Callable:
    """Create fundamentals analyst node.

    Args:
        llm: Language model instance (optional)

    Returns:
        Node function for LangGraph workflow
    """
    # Load template dynamically from TemplateManager
    prompt_template = get_prompt_template(AgentType.FUNDAMENTALS_ANALYST)
    
    return create_analyst_node(
        analyst_type="fundamentals",
        prompt_template=prompt_template,
        llm=llm,
        report_key="fundamentals_report",
    )
