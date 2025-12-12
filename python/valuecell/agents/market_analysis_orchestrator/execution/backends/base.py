"""Base classes and interfaces for execution backends.

This module defines the core abstractions for execution backends that can
be selected by the Trader AI to execute trading decisions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionDecision(BaseModel):
    """Trader AI's execution decision.

    Contains the action to take, which backend to use, and any
    backend-specific parameters.
    """

    backend_id: str = Field(..., description="Selected execution backend ID")
    action: str = Field(
        ..., description="Action to take: buy, sell, hold, or delegate"
    )
    symbol: str = Field(..., description="Trading symbol")
    quantity: Optional[float] = Field(None, description="Trade quantity if applicable")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific parameters"
    )
    rationale: str = Field(..., description="Reasoning for this decision and backend choice")


class ExecutionResult(BaseModel):
    """Result from executing a decision through a backend."""

    success: bool = Field(..., description="Whether execution succeeded")
    backend_id: str = Field(..., description="Backend that executed the decision")
    trades: List[Dict[str, Any]] = Field(
        default_factory=list, description="Executed trades"
    )
    message: str = Field(..., description="Human-readable result message")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional execution metadata"
    )


class ExecutionBackend(ABC):
    """Abstract base class for execution backends.

    Each backend represents a different way to execute trading decisions:
    - DirectOrderBackend: Simple direct order execution
    - PromptStrategyBackend: Delegate to prompt_strategy_agent
    - QuantStrategyBackend: Use Nautilus quantitative strategies
    - GridStrategyBackend: Use grid trading strategies

    Backends declare their capabilities so the Trader AI can make
    informed decisions about which backend to use.
    """

    @property
    @abstractmethod
    def backend_id(self) -> str:
        """Unique identifier for this backend."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this backend."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of this backend's purpose (for Trader AI selection)."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of capability tags for this backend.

        Examples: ["spot", "futures", "grid", "dca", "momentum", "llm_driven"]
        """
        ...

    @abstractmethod
    async def execute(
        self, decision: ExecutionDecision, context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute a trading decision.

        Args:
            decision: The execution decision from Trader AI
            context: Additional context (analysis results, market data, etc.)

        Returns:
            ExecutionResult with success status and any executed trades
        """
        ...

    def supports(self, decision: ExecutionDecision) -> bool:
        """Check if this backend supports the given decision.

        Override to add validation logic. Default returns True.

        Args:
            decision: The decision to check

        Returns:
            True if this backend can handle the decision
        """
        return True

    def to_prompt_section(self) -> str:
        """Generate a prompt section describing this backend for LLM selection.

        Returns:
            Formatted string for inclusion in Trader AI's prompt
        """
        return (
            f"### {self.backend_id}: {self.name}\n"
            f"Description: {self.description}\n"
            f"Capabilities: {', '.join(self.capabilities)}"
        )
