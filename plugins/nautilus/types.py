"""Type definitions for Nautilus Plugin.

This module provides structured type definitions using TypedDict
for better type safety and IDE support.
"""

from typing import TypedDict, Optional


class Bar(TypedDict):
    """OHLCV bar data structure."""
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: float
    symbol: str


class Quote(TypedDict):
    """Quote (bid/ask) data structure."""
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    timestamp: float
    symbol: str


class Trade(TypedDict):
    """Trade tick data structure."""
    price: float
    size: float
    side: str  # 'buy' or 'sell'
    timestamp: float
    symbol: str


class Position(TypedDict):
    """Position data structure."""
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    quantity: float
    entry_price: float
    unrealized_pnl: Optional[float]
    entry_time: float


class Order(TypedDict):
    """Order data structure."""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: Optional[float]
    order_type: str  # 'market' or 'limit'
    status: str  # 'submitted', 'filled', 'cancelled'
    filled_price: Optional[float]
    timestamp: float
