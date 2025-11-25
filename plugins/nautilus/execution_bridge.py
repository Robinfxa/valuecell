"""Execution Bridge - ValueCell Integration.

This module provides the bridge between Nautilus trading signals
and ValueCell order execution. It translates signals into ValueCell
orders and handles execution feedback.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional
import time

from valuecell.plugins.nautilus.signals import TradingSignal, SignalResult, SignalAction


class ExecutionBridge(ABC):
    """
    Abstract base class for execution bridges.
    
    An execution bridge receives trading signals from Nautilus strategies
    and executes them via an external trading system (ValueCell).
    """
    
    @abstractmethod
    async def execute_signal(self, signal: TradingSignal) -> SignalResult:
        """Execute a trading signal.
        
        Args:
            signal: Trading signal to execute
            
        Returns:
            Execution result
        """
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[dict]:
        """Get current position for a symbol.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Position dict or None
        """
        pass


class MockValueCellBridge(ExecutionBridge):
    """
    Mock implementation of ValueCell execution bridge.
    
    This simulates ValueCell order execution for testing purposes.
    In Phase 2+, this will be replaced with real ValueCell API calls.
    """
    
    def __init__(self):
        """Initialize mock bridge."""
        self.orders = []
        self.positions = {}
        self._order_counter = 0
    
    async def execute_signal(self, signal: TradingSignal) -> SignalResult:
        """Execute signal (mock implementation).
        
        Args:
            signal: Trading signal
            
        Returns:
            Mock execution result
        """
        try:
            # Simulate order execution
            order_id = f"vc_order_{self._order_counter}"
            self._order_counter += 1
            
            # Create mock order
            order = {
                "order_id": order_id,
                "signal_id": signal.signal_id,
                "strategy_id": signal.strategy_id,
                "symbol": signal.symbol,
                "action": signal.action.value,
                "quantity": signal.quantity,
                "order_type": signal.order_type,
                "price": signal.price,
                "status": "FILLED",  # Mock always fills
                "filled_price": signal.price or 95000.0,
                "timestamp": time.time()
            }
            
            self.orders.append(order)
            
            # Update mock positions
            self._update_position(signal)
            
            return SignalResult(
                signal_id=signal.signal_id,
                success=True,
                order_id=order_id,
                metadata={"mock": True, "order": order}
            )
            
        except Exception as e:
            return SignalResult(
                signal_id=signal.signal_id,
                success=False,
                error_message=str(e)
            )
    
    async def get_position(self, symbol: str) -> Optional[dict]:
        """Get mock position.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Mock position or None
        """
        return self.positions.get(symbol)
    
    def _update_position(self, signal: TradingSignal):
        """Update mock position based on signal."""
        symbol = signal.symbol
        
        if signal.action == SignalAction.BUY:
            # Add to long position
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "symbol": symbol,
                    "side": "LONG",
                    "quantity": 0.0,
                    "entry_price": signal.price or 95000.0
                }
            self.positions[symbol]["quantity"] += signal.quantity
            
        elif signal.action == SignalAction.SELL:
            # Add to short or reduce long
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "symbol": symbol,
                    "side": "SHORT",
                    "quantity": 0.0,
                    "entry_price": signal.price or 95000.0
                }
            self.positions[symbol]["quantity"] += signal.quantity
            
        elif signal.action == SignalAction.CLOSE_ALL:
            # Close position
            if symbol in self.positions:
                del self.positions[symbol]
    
    def get_all_orders(self):
        """Get all orders."""
        return self.orders


class SignalExecutor:
    """
    Signal executor managing the signal → execution flow.
    
    This class:
    1. Receives signals from strategies
    2. Forwards them to the execution bridge
    3. Handles execution results and feedback
    """
    
    def __init__(self, bridge: ExecutionBridge):
        """Initialize signal executor.
        
        Args:
            bridge: Execution bridge to use
        """
        self.bridge = bridge
        self.signal_queue = asyncio.Queue()
        self.execution_results = []
        self._running = False
        self._task = None
    
    def handle_signal(self, signal: TradingSignal):
        """Handle a trading signal (synchronous).
        
        This is called by strategies. It queues the signal
        for async processing.
        
        Args:
            signal: Trading signal to process
        """
        try:
            # Try to queue signal
            self.signal_queue.put_nowait(signal)
        except asyncio.QueueFull:
            print(f"Warning: Signal queue full, dropping signal {signal.signal_id}")
    
    async def start(self):
        """Start processing signals."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._process_signals())
    
    async def stop(self):
        """Stop processing signals."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _process_signals(self):
        """Process signals from queue."""
        while self._running:
            try:
                # Get signal from queue (with timeout)
                try:
                    signal = await asyncio.wait_for(
                        self.signal_queue.get(),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Execute signal
                result = await self.bridge.execute_signal(signal)
                
                # Record result
                self.execution_results.append(result)
                
                # Log
                if result.success:
                    print(f"✅ Signal executed: {signal.signal_id} → Order {result.order_id}")
                else:
                    print(f"❌ Signal failed: {signal.signal_id} - {result.error_message}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing signal: {e}")
    
    def get_execution_summary(self) -> dict:
        """Get execution statistics.
        
        Returns:
            Summary dict with success/failure counts
        """
        total = len(self.execution_results)
        successful = sum(1 for r in self.execution_results if r.success)
        failed = total - successful
        
        return {
            "total_signals": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0
        }
