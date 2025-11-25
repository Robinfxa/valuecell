"""Signal-Based Strategy Framework.

This module provides base classes for Nautilus strategies that generate
trading signals instead of directly executing orders. This allows for
clean separation between strategy logic (Nautilus) and order execution (ValueCell).
"""

from abc import abstractmethod
from typing import Callable, Optional

from valuecell.plugins.nautilus.signals import TradingSignal, SignalAction


class SignalBasedStrategy:
    """
    Base class for signal-based strategies.
    
    Strategies inheriting from this class generate trading signals
    instead of directly placing orders. Signals are emitted to a
    signal handler which forwards them to the execution bridge.
    
    This design separates:
    - Strategy logic (in Nautilus)
    - Order execution (in ValueCell)
    
    Example:
        >>> class MyStrategy(SignalBasedStrategy):
        ...     def on_data(self, data):
        ...         if self.should_buy(data):
        ...             self.emit_buy_signal("BTC/USDT", 0.01, reason="Bullish signal")
    """
    
    def __init__(self, strategy_id: str, **config):
        """Initialize signal-based strategy.
        
        Args:
            strategy_id: Unique strategy identifier
            **config: Strategy configuration parameters
        """
        self.strategy_id = strategy_id
        self.config = config
        self.is_running = False
        
        # Signal handler (injected externally)
        self._signal_handler: Optional[Callable] = None
        
        # Internal state
        self._positions = {}  # Track virtual positions
        self._signals_emitted = []
    
    def set_signal_handler(self, handler: Callable[[TradingSignal], None]):
        """Set the signal handler.
        
        Args:
            handler: Async function to handle emitted signals
        """
        self._signal_handler = handler
    
    def emit_signal(self, signal: TradingSignal):
        """Emit a trading signal.
        
        Args:
            signal: Trading signal to emit
        """
        if not self._signal_handler:
            raise RuntimeError(
                "Signal handler not set. Call set_signal_handler() first."
            )
        
        # Record signal
        self._signals_emitted.append(signal)
        
        # Send to handler
        self._signal_handler(signal)
    
    def emit_buy_signal(
        self,
        symbol: str,
        quantity: float,
        **kwargs
    ):
        """Emit a BUY signal.
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            **kwargs: Additional signal parameters (price, reason, etc.)
        """
        signal = TradingSignal.create_buy_signal(
            symbol=symbol,
            quantity=quantity,
            strategy_id=self.strategy_id,
            **kwargs
        )
        self.emit_signal(signal)
    
    def emit_sell_signal(
        self,
        symbol: str,
        quantity: float,
        **kwargs
    ):
        """Emit a SELL signal.
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            **kwargs: Additional signal parameters
        """
        signal = TradingSignal.create_sell_signal(
            symbol=symbol,
            quantity=quantity,
            strategy_id=self.strategy_id,
            **kwargs
        )
        self.emit_signal(signal)
    
    def emit_close_signal(
        self,
        symbol: str,
        **kwargs
    ):
        """Emit a CLOSE position signal.
        
        Args:
            symbol: Trading pair to close
            **kwargs: Additional signal parameters
        """
        signal = TradingSignal.create_close_signal(
            symbol=symbol,
            strategy_id=self.strategy_id,
            **kwargs
        )
        self.emit_signal(signal)
    
    def update_position(self, symbol: str, quantity: float, side: str):
        """Update virtual position tracking.
        
        Called by the execution bridge after successful order execution.
        
        Args:
            symbol: Trading pair
            quantity: Position quantity (signed: + for long, - for short)
            side: Position side (LONG/SHORT)
        """
        self._positions[symbol] = {
            "quantity": quantity,
            "side": side
        }
    
    def get_position(self, symbol: str) -> Optional[dict]:
        """Get current virtual position.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Position dict or None if no position
        """
        return self._positions.get(symbol)
    
    def start(self):
        """Start the strategy."""
        self.is_running = True
        self.on_start()
    
    def stop(self):
        """Stop the strategy."""
        self.is_running = False
        self.on_stop()
    
    # Lifecycle hooks (to be overridden by subclasses)
    
    def on_start(self):
        """Called when strategy starts."""
        pass
    
    def on_stop(self):
        """Called when strategy stops."""
        pass
    
    @abstractmethod
    def on_data(self, data: dict):
        """Called when new market data arrives.
        
        Args:
            data: Market data (tick/bar/etc)
        """
        pass
    
    # Prevent direct order methods (enforce signal-based approach)
    
    def buy(self, *args, **kwargs):
        """Disabled. Use emit_buy_signal() instead."""
        raise NotImplementedError(
            "SignalBasedStrategy does not support direct buy(). "
            "Use emit_buy_signal() to generate a trading signal."
        )
    
    def sell(self, *args, **kwargs):
        """Disabled. Use emit_sell_signal() instead."""
        raise NotImplementedError(
            "SignalBasedStrategy does not support direct sell(). "
            "Use emit_sell_signal() to generate a trading signal."
        )
    
    def __repr__(self):
        return f"<SignalBasedStrategy: {self.strategy_id}>"


class SimpleEMACrossSignalStrategy(SignalBasedStrategy):
    """
    Example: Simple EMA crossover strategy using signal-based approach.
    
    This is a demonstration strategy showing how to use SignalBasedStrategy.
    """
    
    def __init__(
        self,
        strategy_id: str = "ema_cross_signal",
        fast_period: int = 10,
        slow_period: int = 30,
        **config
    ):
        super().__init__(strategy_id, **config)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # Price history for EMA calculation
        self._price_history = []
        self._last_signal = None
    
    def on_data(self, data: dict):
        """Process market data and generate signals."""
        if not self.is_running:
            return
        
        # Extract price
        price = data.get("ask", data.get("price", 0))
        if price <= 0:
            return
        
        # Update history
        self._price_history.append(price)
        if len(self._price_history) > self.slow_period:
            self._price_history.pop(0)
        
        # Need enough data
        if len(self._price_history) < self.slow_period:
            return
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(self.fast_period)
        slow_ema = self._calculate_ema(self.slow_period)
        
        symbol = data.get("symbol", "BTC/USDT")
        
        # Check for crossover
        if fast_ema > slow_ema and self._last_signal != "BUY":
            # Bullish crossover
            self.emit_buy_signal(
                symbol=symbol,
                quantity=0.01,  # Fixed position size for demo
                reason=f"EMA bullish cross: {fast_ema:.2f} > {slow_ema:.2f}",
                confidence=0.8,
                metadata={"fast_ema": fast_ema, "slow_ema": slow_ema}
            )
            self._last_signal = "BUY"
            
        elif fast_ema < slow_ema and self._last_signal != "SELL":
            # Bearish crossover
            self.emit_sell_signal(
                symbol=symbol,
                quantity=0.01,
                reason=f"EMA bearish cross: {fast_ema:.2f} < {slow_ema:.2f}",
                confidence=0.8,
                metadata={"fast_ema": fast_ema, "slow_ema": slow_ema}
            )
            self._last_signal = "SELL"
    
    def _calculate_ema(self, period: int) -> float:
        """Calculate EMA for given period."""
        if len(self._price_history) < period:
            return sum(self._price_history) / len(self._price_history)
        
        prices = self._price_history[-period:]
        multiplier = 2 / (period + 1)
        
        # Start with SMA
        ema = sum(prices[:period]) / period
        
        # Calculate EMA
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
