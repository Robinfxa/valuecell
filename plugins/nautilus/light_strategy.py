"""Lightweight Strategy Framework with Indicators.

This module extends SignalBasedStrategy with indicator support and
bar/quote handling, providing a lightweight alternative to full Nautilus.
"""

from typing import Optional, Dict, Any, Callable
import pandas as pd
import ta  # Technical Analysis library

from valuecell.plugins.nautilus.signal_strategy import SignalBasedStrategy


class LightStrategy(SignalBasedStrategy):
    """
    Lightweight strategy framework with indicator support.
    
    Key features:
    - Built on SignalBasedStrategy (signal-driven)
    - Integrated technical indicators (via `ta` library)
    - Bar and quote data handling
    - Suitable for backtesting and live trading
    
    Example:
        >>> class MyStrategy(LightStrategy):
        ...     def on_start(self):
        ...         self.ema_fast = 10
        ...         self.ema_slow = 30
        ...         self.prices = []
        ... 
        ...     def on_bar(self, bar):
        ...         self.prices.append(bar['close'])
        ...         if len(self.prices) < self.ema_slow:
        ...             return
        ...         
        ...         df = pd.DataFrame({'close': self.prices})
        ...         ema_fast = ta.trend.ema_indicator(df['close'], self.ema_fast).iloc[-1]
        ...         ema_slow = ta.trend.ema_indicator(df['close'], self.ema_slow).iloc[-1]
        ...         
        ...         if ema_fast > ema_slow:
        ...             self.emit_buy_signal(bar['symbol'], 0.01)
    """
    
    def __init__(self, strategy_id: str, **config):
        """Initialize lightweight strategy.
        
        Args:
            strategy_id: Unique strategy identifier
            **config: Strategy configuration
        """
        super().__init__(strategy_id, **config)
        
        # Price history for indicators
        self._price_history = []
        self._bar_history = []
        self._quote_history = []
        
        # Indicator cache
        self._indicators: Dict[str, Any] = {}
    
    # Data handlers (override in subclass)
    
    def on_bar(self, bar: dict):
        """Called when a new bar arrives.
        
        Args:
            bar: Bar data dict with keys: open, high, low, close, volume, timestamp, symbol
        """
        self._bar_history.append(bar)
        self._price_history.append(bar.get('close', 0))
    
    def on_quote(self, quote: dict):
        """Called when a new quote arrives.
        
        Args:
            quote: Quote data dict with keys: bid, ask, bid_size, ask_size, timestamp, symbol
        """
        self._quote_history.append(quote)
        mid_price = (quote.get('bid', 0) + quote.get('ask', 0)) / 2
        if mid_price > 0:
            self._price_history.append(mid_price)
    
    def on_trade(self, trade: dict):
        """Called when a trade tick arrives.
        
        Args:
            trade: Trade data dict with keys: price, size, side, timestamp, symbol
        """
        price = trade.get('price', 0)
        if price > 0:
            self._price_history.append(price)
    
    # Indicator helpers
    
    def get_dataframe(self, length: Optional[int] = None) -> pd.DataFrame:
        """Get price history as DataFrame for indicator calculation.
        
        Args:
            length: Number of recent bars to include (None = all)
            
        Returns:
            DataFrame with OHLCV data (if available) or just close prices
        """
        if self._bar_history:
            bars = self._bar_history[-length:] if length else self._bar_history
            return pd.DataFrame(bars)
        else:
            prices = self._price_history[-length:] if length else self._price_history
            return pd.DataFrame({'close': prices})
    
    def calculate_ema(self, period: int, prices: Optional[list] = None) -> Optional[float]:
        """Calculate EMA indicator.
        
        Args:
            period: EMA period
            prices: Price list (default: use strategy's price history)
            
        Returns:
            Current EMA value or None if insufficient data
        """
        price_data = prices if prices is not None else self._price_history
        
        if len(price_data) < period:
            return None
        
        df = pd.DataFrame({'close': price_data})
        ema = ta.trend.ema_indicator(df['close'], window=period)
        return float(ema.iloc[-1]) if not ema.empty else None
    
    def calculate_rsi(self, period: int = 14, prices: Optional[list] = None) -> Optional[float]:
        """Calculate RSI indicator.
        
        Args:
            period: RSI period
            prices: Price list
            
        Returns:
            Current RSI value (0-100) or None
        """
        price_data = prices if prices is not None else self._price_history
        
        if len(price_data) < period + 1:
            return None
        
        df = pd.DataFrame({'close': price_data})
        rsi = ta.momentum.rsi(df['close'], window=period)
        return float(rsi.iloc[-1]) if not rsi.empty else None
    
    def calculate_macd(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        prices: Optional[list] = None
    ) -> Optional[Dict[str, float]]:
        """Calculate MACD indicator.
        
        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            prices: Price list
            
        Returns:
            Dict with 'macd', 'signal', 'histogram' or None
        """
        price_data = prices if prices is not None else self._price_history
        
        if len(price_data) < slow + signal:
            return None
        
        df = pd.DataFrame({'close': price_data})
        macd_obj = ta.trend.MACD(df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
        
        return {
            'macd': float(macd_obj.macd().iloc[-1]),
            'signal': float(macd_obj.macd_signal().iloc[-1]),
            'histogram': float(macd_obj.macd_diff().iloc[-1])
        }
    
    def calculate_bollinger_bands(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        prices: Optional[list] = None
    ) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands.
        
        Args:
            period: SMA period
            std_dev: Standard deviation multiplier
            prices: Price list
            
        Returns:
            Dict with 'upper', 'middle', 'lower' or None
        """
        price_data = prices if prices is not None else self._price_history
        
        if len(price_data) < period:
            return None
        
        df = pd.DataFrame({'close': price_data})
        bb = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std_dev)
        
        return {
            'upper': float(bb.bollinger_hband().iloc[-1]),
            'middle': float(bb.bollinger_mavg().iloc[-1]),
            'lower': float(bb.bollinger_lband().iloc[-1])
        }
    
    # Utility methods
    
    def get_last_price(self) -> Optional[float]:
        """Get most recent price."""
        return self._price_history[-1] if self._price_history else None
    
    def get_price_history(self, length: Optional[int] = None) -> list:
        """Get price history.
        
        Args:
            length: Number of recent prices (None = all)
            
        Returns:
            List of prices
        """
        if length is None:
            return self._price_history.copy()
        return self._price_history[-length:]
    
    def clear_history(self):
        """Clear all history (useful for testing)."""
        self._price_history.clear()
        self._bar_history.clear()
        self._quote_history.clear()
        self._indicators.clear()
