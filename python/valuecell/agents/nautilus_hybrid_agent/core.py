"""Nautilus Hybrid Agent - Mixed LLM and Rule-Based Trading.

This agent combines LLM-driven market analysis with rule-based trading strategies,
providing three operational modes: pure LLM, fixed rule strategy, and hybrid mode
where LLM intelligently selects strategies based on market conditions.
"""

from __future__ import annotations

from typing import Optional

from loguru import logger

from valuecell.agents.common.trading.base_agent import BaseStrategyAgent
from valuecell.agents.common.trading.models import UserRequest
from valuecell.plugins.nautilus.hybrid_composer import HybridComposer
from valuecell.plugins.nautilus.strategy_registry import register_default_strategies


class NautilusHybridAgent(BaseStrategyAgent):
    """Nautilus hybrid trading agent.
    
    Extends BaseStrategyAgent to provide hybrid decision making through three modes:
    1. LLM mode: Pure LLM-based market analysis and trade generation
    2. Rule mode: Fixed rule-based strategy execution
    3. Hybrid mode: LLM selects strategy, rules execute trades
    
    The agent integrates seamlessly with ValueCell's trading infrastructure,
    leveraging existing execution, portfolio, and risk management systems.
    """
    
    def __init__(self, **kwargs):
        """Initialize Nautilus hybrid agent.
        
        Registers default Nautilus strategies (EMA, RSI, BB) on initialization.
        """
        super().__init__(**kwargs)
        
        # Register default strategies to make them available for selection
        register_default_strategies()
        
        logger.info("NautilusHybridAgent initialized")
    
    async def _build_features_pipeline(
        self,
        request: UserRequest
    ) -> Optional[object]:
        """Use ValueCell's default features pipeline.
        
        Returns None to use ValueCell's DefaultFeaturesPipeline which provides:
        - CCXT-based market data fetching
        - OHLCV candle aggregation
        - Market snapshot data
        
        Args:
            request: User request with trading configuration
            
        Returns:
            None to use default pipeline
        """
        return None
    
    async def _create_decision_composer(
        self,
        request: UserRequest
    ) -> Optional[object]:
        """Create hybrid decision composer.
        
        This is the core integration point where we inject our custom
        hybrid decision logic into ValueCell's trading framework.
        
        Args:
            request: User request with decision_mode configuration
            
        Returns:
            HybridComposer instance
        """
        return HybridComposer(request)
    
    async def _on_start(self, runtime, request):
        """Called when strategy starts.
        
        Args:
            runtime: StrategyRuntime instance
            request: UserRequest
        """
        mode = getattr(request.trading_config, 'decision_mode', 'hybrid')
        
        logger.info(
            "Nautilus Hybrid Agent started",
            strategy_id=runtime.strategy_id,
            decision_mode=mode,
            symbols=request.trading_config.symbols,
            initial_capital=request.trading_config.initial_capital
        )
    
    async def _on_cycle_result(self, result, runtime, request):
        """Called after each decision cycle completes.
        
        Args:
            result: DecisionCycleResult with trades and metadata
            runtime: StrategyRuntime instance
            request: UserRequest
        """
        metadata = getattr(result, 'metadata', {})
        
        logger.info(
            "Decision cycle complete",
            strategy_id=runtime.strategy_id,
            trades_count=len(result.trades) if hasattr(result, 'trades') else 0,
            decision_mode=metadata.get('decision_mode'),
            selected_strategy=metadata.get('selected_strategy'),
            market_condition=metadata.get('market_condition')
        )
    
    async def _on_stop(self, runtime, request, reason):
        """Called when strategy stops.
        
        Args:
            runtime: StrategyRuntime instance
            request: UserRequest
            reason: StopReason (normal_exit, cancelled, error, etc.)
        """
        logger.info(
            "Nautilus Hybrid Agent stopped",
            strategy_id=runtime.strategy_id,
            reason=str(reason)
        )
