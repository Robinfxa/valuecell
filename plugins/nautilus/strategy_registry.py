"""Strategy Registry for Hybrid Decision Framework.

This module provides a centralized registry for rule-based trading strategies,
allowing LLM to query and select strategies based on market conditions.
"""

from typing import Dict, Type, List, Optional
from dataclasses import dataclass
from loguru import logger

from valuecell.plugins.nautilus.light_strategy import LightStrategy


@dataclass
class StrategyMetadata:
    """Metadata describing a trading strategy for LLM selection.
    
    Attributes:
        strategy_id: Unique identifier
        name: Human-readable name
        description: Strategy description
        best_for: Market conditions this strategy excels in
        indicators: Technical indicators used
        timeframes: Suitable timeframes
        risk_level: Risk assessment (low/medium/high)
        strategy_class: Strategy implementation class
    """
    strategy_id: str
    name: str
    description: str
    best_for: List[str]
    indicators: List[str]
    timeframes: List[str]
    risk_level: str
    strategy_class: Type[LightStrategy]


class StrategyRegistry:
    """Centralized registry for trading strategies.
    
    Manages strategy metadata and provides query interface for LLM
    to select appropriate strategies based on market conditions.
    """
    
    def __init__(self):
        self._strategies: Dict[str, StrategyMetadata] = {}
        logger.info("StrategyRegistry initialized")
    
    def register(self, metadata: StrategyMetadata) -> None:
        """Register a strategy with metadata.
        
        Args:
            metadata: Strategy metadata to register
        """
        self._strategies[metadata.strategy_id] = metadata
        logger.info(
            "Registered strategy",
            strategy_id=metadata.strategy_id,
            name=metadata.name
        )
    
    def get(self, strategy_id: str) -> Optional[StrategyMetadata]:
        """Get strategy metadata by ID.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy metadata or None if not found
        """
        return self._strategies.get(strategy_id)
    
    def list_all(self) -> List[StrategyMetadata]:
        """List all registered strategies.
        
        Returns:
            List of all strategy metadata
        """
        return list(self._strategies.values())
    
    def query(
        self,
        market_condition: Optional[str] = None,
        timeframe: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[StrategyMetadata]:
        """Query strategies by conditions.
        
        Args:
            market_condition: Market condition filter (trending/ranging/volatile)
            timeframe: Timeframe filter (1m/5m/1h/etc)
            risk_level: Risk level filter (low/medium/high)
            
        Returns:
            List of matching strategies
        """
        results = self.list_all()
        
        if market_condition:
            results = [
                s for s in results
                if market_condition in s.best_for
            ]
        
        if timeframe:
            results = [
                s for s in results
                if timeframe in s.timeframes
            ]
        
        if risk_level:
            results = [
                s for s in results
                if s.risk_level == risk_level
            ]
        
        logger.debug(
            "Strategy query",
            condition=market_condition,
            timeframe=timeframe,
            risk=risk_level,
            results=len(results)
        )
        
        return results
    
    def to_llm_prompt(self) -> str:
        """Generate LLM-readable strategy descriptions.
        
        Returns:
            Formatted string describing all available strategies
        """
        if not self._strategies:
            return "No strategies available"
        
        lines = ["Available Trading Strategies:\n"]
        
        for i, strategy in enumerate(self.list_all(), 1):
            lines.append(f"{i}. {strategy.name} (ID: {strategy.strategy_id})")
            lines.append(f"   Description: {strategy.description}")
            lines.append(f"   Best for: {', '.join(strategy.best_for)}")
            lines.append(f"   Indicators: {', '.join(strategy.indicators)}")
            lines.append(f"   Timeframes: {', '.join(strategy.timeframes)}")
            lines.append(f"   Risk Level: {strategy.risk_level}")
            lines.append("")
        
        return "\n".join(lines)


# Global registry instance
_global_registry = StrategyRegistry()


def get_registry() -> StrategyRegistry:
    """Get the global strategy registry.
    
    Returns:
        Global StrategyRegistry instance
    """
    return _global_registry


def register_default_strategies():
    """Register built-in strategies.
    
    This function registers all default Nautilus strategies with their metadata.
    Should be called during plugin initialization.
    """
    from valuecell.plugins.nautilus.examples.ema_strategy import EMAStrategy
    from valuecell.plugins.nautilus.examples.rsi_strategy import RSIStrategy
    from valuecell.plugins.nautilus.examples.bb_strategy import BBStrategy
    
    registry = get_registry()
    
    # EMA Cross Strategy
    registry.register(StrategyMetadata(
        strategy_id="ema_cross",
        name="EMA Cross Strategy",
        description="Trend-following strategy using fast/slow EMA crossovers. "
                    "Generates buy signals on golden cross and sell on death cross.",
        best_for=["trending", "breakout", "momentum"],
        indicators=["EMA_fast", "EMA_slow"],
        timeframes=["5m", "15m", "1h", "4h", "1d"],
        risk_level="medium",
        strategy_class=EMAStrategy
    ))
    
    # RSI Mean Reversion
    registry.register(StrategyMetadata(
        strategy_id="rsi_mean_reversion",
        name="RSI Mean Reversion",
        description="Counter-trend strategy for ranging markets. "
                    "Buys in oversold territory (RSI<30) and sells in overbought (RSI>70).",
        best_for=["ranging", "oversold", "overbought", "sideways"],
        indicators=["RSI"],
        timeframes=["1m", "5m", "15m", "1h"],
        risk_level="high",
        strategy_class=RSIStrategy
    ))
    
    # Bollinger Bands Reversal
    registry.register(StrategyMetadata(
        strategy_id="bb_reversal",
        name="Bollinger Bands Reversal",
        description="Volatility-based mean reversion strategy. "
                    "Trades reversals when price touches upper/lower bands.",
        best_for=["ranging", "volatile", "mean_reversion"],
        indicators=["BB_upper", "BB_middle", "BB_lower"],
        timeframes=["5m", "15m", "1h", "4h"],
        risk_level="medium",
        strategy_class=BBStrategy
    ))
    
    logger.info(
        "Registered default strategies",
        count=len(registry.list_all())
    )
