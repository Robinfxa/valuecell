"""Base classes for prompt templates.

Provides abstractions for managing and customizing prompts
for each internal agent in the analysis workflow.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from loguru import logger


@dataclass
class PromptTemplate:
    """A reusable prompt template with variable substitution.

    Attributes:
        id: Unique identifier
        name: Human-readable name
        agent_type: Type of agent this template is for
        content: The prompt template with {variable} placeholders
        variables: List of required variable names
        description: Optional description
        is_default: Whether this is the default template
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str
    name: str
    agent_type: str
    content: str
    variables: List[str] = field(default_factory=list)
    description: str = ""
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables.

        Args:
            **kwargs: Variable values to substitute

        Returns:
            Rendered prompt string

        Raises:
            ValueError: If required variables are missing
        """
        # Check for missing variables
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            logger.warning(f"Missing template variables: {missing}")
            # Fill with placeholder instead of failing
            for m in missing:
                kwargs[m] = f"[{m}]"

        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            logger.exception(f"Template rendering error: {e}")
            return self.content

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "content": self.content,
            "variables": self.variables,
            "description": self.description,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            agent_type=data["agent_type"],
            content=data["content"],
            variables=data.get("variables", []),
            description=data.get("description", ""),
            is_default=data.get("is_default", False),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(),
        )


@dataclass
class TemplateSet:
    """A collection of templates forming a complete analysis strategy.

    Allows switching between different "personality sets" for
    all agents at once (e.g., "aggressive trading" vs "conservative").
    """

    id: str
    name: str
    description: str = ""
    template_ids: Dict[str, str] = field(default_factory=dict)  # agent_type -> template_id
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template_ids": self.template_ids,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateSet":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            template_ids=data.get("template_ids", {}),
            is_default=data.get("is_default", False),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


# Agent type constants
class AgentType:
    """Constants for agent types."""

    MARKET_ANALYST = "market_analyst"
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    NEWS_ANALYST = "news_analyst"
    SOCIAL_ANALYST = "social_analyst"
    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    RESEARCH_MANAGER = "research_manager"
    RISKY_DEBATER = "risky_debater"
    SAFE_DEBATER = "safe_debater"
    NEUTRAL_DEBATER = "neutral_debater"
    RISK_MANAGER = "risk_manager"
    TRADER_AI = "trader_ai"

    ALL = [
        MARKET_ANALYST,
        FUNDAMENTALS_ANALYST,
        NEWS_ANALYST,
        SOCIAL_ANALYST,
        BULL_RESEARCHER,
        BEAR_RESEARCHER,
        RESEARCH_MANAGER,
        RISKY_DEBATER,
        SAFE_DEBATER,
        NEUTRAL_DEBATER,
        RISK_MANAGER,
        TRADER_AI,
    ]
