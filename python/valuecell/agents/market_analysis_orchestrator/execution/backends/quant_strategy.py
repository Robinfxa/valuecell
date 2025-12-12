"""Quantitative Strategy Execution Backend.

Delegates trading decisions to Nautilus quantitative strategies
for rule-based, backtested execution.
"""

from typing import Any, Dict, List

from loguru import logger

from .base import ExecutionBackend, ExecutionDecision, ExecutionResult


class QuantStrategyBackend(ExecutionBackend):
    """Nautilus quantitative strategy execution backend.

    Uses rule-based quantitative strategies (EMA, RSI, Bollinger, etc.)
    from the Nautilus integration for systematic execution.

    Best for:
    - Clear trending markets
    - High-frequency decision making
    - Backtested strategy execution
    """

    SUPPORTED_STRATEGIES = [
        "ema_cross",
        "rsi",
        "bollinger_bands",
        "macd",
        "momentum",
    ]

    @property
    def backend_id(self) -> str:
        return "quant_nautilus"

    @property
    def name(self) -> str:
        return "Nautilus 量化策略"

    @property
    def description(self) -> str:
        return (
            "使用规则化的量化策略执行交易。适合趋势明确、需要快速响应的"
            "市场环境。支持 EMA 交叉、RSI、布林带、MACD 等多种经过回测验证的策略。"
            "执行速度快，风控规则明确。"
        )

    @property
    def capabilities(self) -> List[str]:
        return ["rule_based", "fast", "backtested", "quantitative", "systematic"]

    async def execute(
        self, decision: ExecutionDecision, context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute via Nautilus quantitative strategy.

        Args:
            decision: The trading decision
            context: Execution context

        Returns:
            ExecutionResult from the quant strategy
        """
        # Get requested strategy ID
        strategy_id = decision.params.get("strategy_id", "ema_cross")

        logger.info(
            "QuantStrategyBackend executing",
            strategy_id=strategy_id,
            action=decision.action,
            symbol=decision.symbol,
        )

        if strategy_id not in self.SUPPORTED_STRATEGIES:
            return ExecutionResult(
                success=False,
                backend_id=self.backend_id,
                message=f"Unknown strategy: {strategy_id}. Supported: {self.SUPPORTED_STRATEGIES}",
            )

        try:
            # TODO: Integrate with actual Nautilus HybridComposer
            # For now, simulate the strategy execution

            # Simulate strategy signal
            trade = {
                "symbol": decision.symbol,
                "side": decision.action.upper() if decision.action in ("buy", "sell") else "NONE",
                "quantity": decision.quantity or 0,
                "status": "SIMULATED",
                "strategy_id": strategy_id,
                "rationale": f"Quant strategy ({strategy_id}): {decision.rationale}",
            }

            return ExecutionResult(
                success=True,
                backend_id=self.backend_id,
                trades=[trade] if decision.action in ("buy", "sell") else [],
                message=f"Executed via {strategy_id} strategy for {decision.symbol}",
                metadata={
                    "strategy_id": strategy_id,
                    "simulated": True,
                },
            )

        except Exception as e:
            logger.exception("QuantStrategyBackend execution failed", error=str(e))
            return ExecutionResult(
                success=False,
                backend_id=self.backend_id,
                message=f"Quant strategy execution failed: {e}",
            )

    def supports(self, decision: ExecutionDecision) -> bool:
        """Check if this backend supports the decision."""
        return decision.action in ("buy", "sell", "hold")
