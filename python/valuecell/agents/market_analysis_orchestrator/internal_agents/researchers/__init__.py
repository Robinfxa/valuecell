"""Researchers package - Bull/Bear debate agents."""

from .bear_researcher import create_bear_researcher
from .bull_researcher import create_bull_researcher
from .research_manager import create_research_manager

__all__ = [
    "create_bull_researcher",
    "create_bear_researcher",
    "create_research_manager",
]
