"""Nautilus Strategy Pool.

This module manages a collection of pre-configured trading strategies
that can be selected and instantiated by ValueCell AI.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


@dataclass
class StrategyDescriptor:
    """
    Strategy descriptor containing metadata about a trading strategy.
    
    This model defines the characteristics and parameters of a strategy
    that can be used by AI to select the most appropriate one.
    """
    
    strategy_id: str
    """Unique identifier for the strategy"""
    
    name: str
    """Human-readable strategy name"""
    
    category: str
    """Strategy category: trend_following | mean_reversion | arbitrage | grid"""
    
    description: str
    """Detailed description of the strategy"""
    
    parameters: Dict[str, Any]
    """Default parameters and their values"""
    
    suitable_markets: List[str]
    """Market conditions where this strategy performs well"""
    
    risk_level: str
    """Risk level: low | medium | high"""
    
    min_capital: float
    """Minimum capital required to run this strategy"""
    
    instrument_type: str = "spot"
    """Instrument type: spot | future | option"""


class DummyStrategy:
    """
    Dummy strategy for testing purposes.
    
    This is a placeholder strategy that doesn't execute any real trading logic.
    It will be replaced by real Nautilus Strategy implementations in Phase 2.2.
    """
    
    def __init__(self, **params):
        """Initialize dummy strategy with parameters.
        
        Args:
            **params: Strategy parameters
        """
        self.params = params
        self.name = params.get("name", "DummyStrategy")
        self.is_running = False
    
    def start(self):
        """Start the strategy."""
        self.is_running = True
    
    def stop(self):
        """Stop the strategy."""
        self.is_running = False
    
    def __repr__(self):
        return f"<DummyStrategy: {self.name}>"


class NautilusStrategyPool:
    """
    Nautilus Strategy Pool.
    
    Responsibilities:
    1. Register and manage pre-configured strategies
    2. Provide strategy query and filtering
    3. Instantiate strategy objects
    4. Strategy version management
    """
    
    def __init__(self):
        """Initialize strategy pool."""
        self.strategies: Dict[str, Type] = {}
        self.descriptors: Dict[str, StrategyDescriptor] = {}
        self._register_builtin_strategies()
    
    def _register_builtin_strategies(self):
        """Register built-in strategies."""
        # Register a dummy strategy for testing
        self.register_strategy(
            "ema_cross",
            DummyStrategy,
            StrategyDescriptor(
                strategy_id="ema_cross",
                name="EMA Cross",
                category="trend_following",
                description="Simple EMA crossover strategy for testing",
                parameters={
                    "fast_ema": 10,
                    "slow_ema": 30,
                    "stop_loss_pct": 0.02,
                    "take_profit_pct": 0.05
                },
                suitable_markets=["单边趋势", "高波动"],
                risk_level="medium",
                min_capital=1000.0,
                instrument_type="spot"
            )
        )
        
        # Register another dummy strategy
        self.register_strategy(
            "bollinger_mean_reversion",
            DummyStrategy,
            StrategyDescriptor(
                strategy_id="bollinger_mean_reversion",
                name="Bollinger Mean Reversion",
                category="mean_reversion",
                description="Bollinger Bands mean reversion strategy",
                parameters={
                    "bb_period": 20,
                    "bb_std": 2.0,
                    "position_size_pct": 0.1
                },
                suitable_markets=["震荡", "低波动"],
                risk_level="low",
                min_capital=500.0,
                instrument_type="spot"
            )
        )
    
    def register_strategy(
        self,
        strategy_id: str,
        strategy_class: Type,
        descriptor: StrategyDescriptor
    ):
        """Register a strategy in the pool.
        
        Args:
            strategy_id: Unique strategy identifier
            strategy_class: Strategy class (must be instantiable)
            descriptor: Strategy descriptor with metadata
        """
        if strategy_id in self.strategies:
            raise ValueError(f"Strategy {strategy_id} already registered")
        
        self.strategies[strategy_id] = strategy_class
        self.descriptors[strategy_id] = descriptor
    
    def list_strategies(
        self,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        market_condition: Optional[str] = None,
        instrument_type: Optional[str] = None
    ) -> List[StrategyDescriptor]:
        """List strategies with optional filtering.
        
        Args:
            category: Filter by category
            risk_level: Filter by risk level
            market_condition: Filter by suitable market condition
            instrument_type: Filter by instrument type
            
        Returns:
            List of matching strategy descriptors
        """
        results = list(self.descriptors.values())
        
        if category:
            results = [s for s in results if s.category == category]
        
        if risk_level:
            results = [s for s in results if s.risk_level == risk_level]
        
        if market_condition:
            results = [
                s for s in results
                if market_condition in s.suitable_markets
            ]
        
        if instrument_type:
            results = [s for s in results if s.instrument_type == instrument_type]
        
        return results
    
    def get_strategy_descriptor(self, strategy_id: str) -> Optional[StrategyDescriptor]:
        """Get descriptor for a specific strategy.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Strategy descriptor or None if not found
        """
        return self.descriptors.get(strategy_id)
    
    def create_strategy_instance(
        self,
        strategy_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Create a strategy instance.
        
        Args:
            strategy_id: Strategy ID to instantiate
            parameters: Optional parameters to override defaults
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy_id not found
        """
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found in pool")
        
        strategy_class = self.strategies[strategy_id]
        descriptor = self.descriptors[strategy_id]
        
        # Merge parameters (override defaults with provided params)
        final_params = descriptor.parameters.copy()
        if parameters:
            final_params.update(parameters)
        
        # Add name to params
        final_params["name"] = descriptor.name
        
        # Instantiate strategy
        return strategy_class(**final_params)
    
    def get_strategy_count(self) -> int:
        """Get total number of registered strategies."""
        return len(self.strategies)
