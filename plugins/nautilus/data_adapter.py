"""Nautilus Data Adapter - Fake Implementation.

This module provides a data adapter that generates fake market data
for testing purposes. It will be replaced with real Nautilus DataEngine
integration in Phase 1.3.
"""

import asyncio
import random
import time
import uuid
from typing import Callable, Dict, Optional


class NautilusDataAdapter:
    """
    Nautilus Data Adapter (Phase 1.1 - Fake Implementation).
    
    Responsibilities:
    1. Generate fake market data (ticks/bars)
    2. Manage subscriptions
    3. Provide ValueCell-compatible data format
    
    This will be replaced with real NautilusTrader DataEngine in Phase 1.3.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the data adapter.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.subscriptions: Dict[str, asyncio.Task] = {}
        self._running = False
    
    async def subscribe_market_data(
        self,
        symbol: str,
        data_type: str,
        callback: Callable
    ) -> str:
        """Subscribe to market data stream.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            data_type: Type of data ("quote" | "trade" | "bar")
            callback: Async callback function to receive data
            
        Returns:
            subscription_id: Unique subscription identifier
            
        Example:
            >>> adapter = NautilusDataAdapter()
            >>> async def on_data(data):
            ...     print(f"Received: {data}")
            >>> sub_id = await adapter.subscribe_market_data(
            ...     "BTC/USDT", "quote", on_data
            ... )
        """
        subscription_id = uuid.uuid4().hex
        
        # Start fake data generator
        task = asyncio.create_task(
            self._fake_data_generator(symbol, data_type, callback)
        )
        
        self.subscriptions[subscription_id] = task
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from market data.
        
        Args:
            subscription_id: Subscription ID to cancel
            
        Returns:
            True if successfully unsubscribed
        """
        if subscription_id in self.subscriptions:
            task = self.subscriptions[subscription_id]
            task.cancel()
            del self.subscriptions[subscription_id]
            return True
        return False
    
    async def _fake_data_generator(
        self,
        symbol: str,
        data_type: str,
        callback: Callable
    ):
        """Generate fake market data.
        
        Args:
            symbol: Trading pair
            data_type: Data type to generate
            callback: Callback to receive data
        """
        # Starting price (BTC)
        base_price = 95000.0 if "BTC" in symbol else 3000.0
        price = base_price
        
        try:
            while True:
                # Random walk
                price += random.uniform(-100, 100)
                
                # Generate fake tick
                tick_data = {
                    "type": data_type,
                    "symbol": symbol,
                    "bid": price - 0.5,
                    "ask": price + 0.5,
                    "bid_size": random.uniform(0.1, 5.0),
                    "ask_size": random.uniform(0.1, 5.0),
                    "timestamp": int(time.time() * 1000)
                }
                
                # Send to callback
                await callback(tick_data)
                
                # Wait 1 second
                await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            # Subscription cancelled
            pass
    
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> list:
        """Get historical bar data (fake implementation).
        
        Args:
            symbol: Trading pair
            timeframe: Bar timeframe (e.g., "1m", "5m", "1h")
            start: Start time (ISO format)
            end: End time (ISO format)
            
        Returns:
            List of bar dictionaries
        """
        # Return empty list for now
        # Will be implemented in Phase 1.3 with real Nautilus data
        return []
    
    def stop(self):
        """Stop all subscriptions."""
        for task in self.subscriptions.values():
            task.cancel()
        self.subscriptions.clear()
