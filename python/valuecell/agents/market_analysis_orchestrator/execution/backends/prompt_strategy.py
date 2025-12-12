"""Prompt Strategy Execution Backend.

Delegates trading decisions to the prompt_strategy_agent for
flexible LLM-driven execution with custom prompts.
"""

from typing import Any, Dict, List

from loguru import logger

from .base import ExecutionBackend, ExecutionDecision, ExecutionResult


class PromptStrategyBackend(ExecutionBackend):
    """Prompt-based strategy execution backend.

    Delegates execution to the prompt_strategy_agent, which uses
    LLM-driven decision making with customizable prompts.

    Best for:
    - Complex market situations requiring nuanced judgment
    - Adapting to rapidly changing conditions
    - Custom strategy templates
    """

    @property
    def backend_id(self) -> str:
        return "prompt_strategy"

    @property
    def name(self) -> str:
        return "提示词策略 AI"

    @property
    def description(self) -> str:
        return (
            "使用 LLM 驱动的提示词策略进行交易执行。适合需要灵活分析和"
            "复杂决策的场景，可以理解市场细微变化。支持自定义提示词模板，"
            "能够根据特定市场条件调整策略行为。"
        )

    @property
    def capabilities(self) -> List[str]:
        return ["flexible", "llm_driven", "custom_prompt", "adaptive", "contextual"]

    async def execute(
        self, decision: ExecutionDecision, context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute via prompt strategy agent.

        Args:
            decision: The trading decision
            context: Execution context including analysis results

        Returns:
            ExecutionResult from the prompt strategy agent
        """
        logger.info(
            "PromptStrategyBackend delegating",
            action=decision.action,
            symbol=decision.symbol,
        )

        # Get custom prompt template if specified
        prompt_template = decision.params.get("prompt_template")

        try:
            # TODO: Integrate with actual prompt_strategy_agent
            # For now, simulate the delegation

            # Build strategy request
            strategy_request = {
                "symbol": decision.symbol,
                "action_hint": decision.action,
                "analysis_context": context.get("analysis_report", {}),
                "risk_context": context.get("risk_assessment", {}),
                "prompt_template": prompt_template,
            }

            logger.debug(
                "Strategy request prepared",
                symbol=decision.symbol,
                has_template=prompt_template is not None,
            )

            # Simulate response from prompt_strategy_agent
            trade = {
                "symbol": decision.symbol,
                "side": decision.action.upper() if decision.action in ("buy", "sell") else "NONE",
                "quantity": decision.quantity or 0,
                "status": "DELEGATED",
                "backend": "prompt_strategy_agent",
                "rationale": decision.rationale,
            }

            return ExecutionResult(
                success=True,
                backend_id=self.backend_id,
                trades=[trade] if decision.action in ("buy", "sell") else [],
                message=f"Delegated to prompt_strategy_agent for {decision.symbol}",
                metadata={
                    "delegated": True,
                    "prompt_template_used": prompt_template is not None,
                },
            )

        except Exception as e:
            logger.exception("PromptStrategyBackend execution failed", error=str(e))
            return ExecutionResult(
                success=False,
                backend_id=self.backend_id,
                message=f"Prompt strategy execution failed: {e}",
            )

    def supports(self, decision: ExecutionDecision) -> bool:
        """Check if this backend supports the decision."""
        # Prompt strategy can handle most decision types
        return decision.action in ("buy", "sell", "hold", "delegate")
