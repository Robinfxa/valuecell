"""Direct Order Execution Backend.

Simple backend that executes direct buy/sell orders without
additional strategy logic. Suitable for simple entries/exits
when the Trader AI has high confidence in the decision.
"""

from typing import Any, Dict, List

from loguru import logger

from .base import ExecutionBackend, ExecutionDecision, ExecutionResult


class DirectOrderBackend(ExecutionBackend):
    """Direct order execution backend.

    Executes simple buy/sell orders directly without intermediate
    strategy logic. Best for:
    - High-confidence decisions from Trader AI
    - Simple position entries/exits
    - Manual override scenarios
    """

    @property
    def backend_id(self) -> str:
        return "direct_order"

    @property
    def name(self) -> str:
        return "直接下单"

    @property
    def description(self) -> str:
        return (
            "直接执行买入/卖出指令，不经过额外策略逻辑。"
            "适合高确信度决策或简单的仓位进出场景。"
            "响应速度最快，但不包含止损/止盈等风控。"
        )

    @property
    def capabilities(self) -> List[str]:
        return ["spot", "direct", "simple", "fast", "manual"]

    async def execute(
        self, decision: ExecutionDecision, context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute a direct order.

        Args:
            decision: The trading decision
            context: Execution context

        Returns:
            ExecutionResult with trade details
        """
        logger.info(
            "DirectOrderBackend executing",
            action=decision.action,
            symbol=decision.symbol,
            quantity=decision.quantity,
        )

        # For now, simulate order execution
        # TODO: Integrate with actual order execution system
        if decision.action == "hold":
            return ExecutionResult(
                success=True,
                backend_id=self.backend_id,
                message="No action taken (hold)",
                metadata={"action": "hold"},
            )

        if decision.action not in ("buy", "sell"):
            return ExecutionResult(
                success=False,
                backend_id=self.backend_id,
                message=f"Unsupported action: {decision.action}",
            )

        # Simulate trade
        trade = {
            "symbol": decision.symbol,
            "side": decision.action.upper(),
            "quantity": decision.quantity or 0,
            "status": "SIMULATED",
            "rationale": decision.rationale,
        }

        return ExecutionResult(
            success=True,
            backend_id=self.backend_id,
            trades=[trade],
            message=f"Direct {decision.action} order placed for {decision.symbol}",
            metadata={"simulated": True},
        )

    def supports(self, decision: ExecutionDecision) -> bool:
        """Check if this backend supports the decision."""
        return decision.action in ("buy", "sell", "hold")
