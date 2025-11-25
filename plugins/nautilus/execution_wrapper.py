"""Nautilus Execution Wrapper - Fake Implementation.

This module provides an execution wrapper that simulates order execution
for testing purposes. It will be replaced with real Nautilus ExecutionEngine
integration in Phase 1.3.
"""

import uuid
from typing import Dict, List, Optional


class NautilusExecutionWrapper:
    """
    Nautilus Execution Wrapper (Phase 1.2 - Fake Implementation).
    
    Responsibilities:
    1. Simulate order submission
    2. Track fake positions
    3. Provide ValueCell-compatible order/position format
    
    This will be replaced with real NautilusTrader ExecutionEngine in Phase 1.3.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the execution wrapper.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.fake_orders: Dict[str, Dict] = {}
        self.fake_positions: List[Dict] = []
        self._order_counter = 0
    
    async def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> dict:
        """Submit an order (fake implementation).
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            side: Order side ("BUY" | "SELL")
            quantity: Order quantity
            order_type: Order type ("MARKET" | "LIMIT")
            price: Limit price (required for LIMIT orders)
            
        Returns:
            Order result dictionary with order_id and status
            
        Example:
            >>> wrapper = NautilusExecutionWrapper()
            >>> result = await wrapper.submit_order(
            ...     "BTC/USDT", "BUY", 0.01, "MARKET"
            ... )
            >>> print(result["order_id"])
        """
        self._order_counter += 1
        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        
        # Determine fill price
        if order_type == "MARKET":
            # Simulate market price
            fill_price = 95000.0 if "BTC" in symbol else 3000.0
        else:
            # Use limit price
            fill_price = price if price else 95000.0
        
        # Create fake order
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "status": "FILLED",  # Fake orders fill immediately
            "filled_price": fill_price,
            "filled_qty": quantity,
            "created_at": self._get_timestamp()
        }
        
        self.fake_orders[order_id] = order
        
        # Update positions
        self._update_positions(symbol, side, quantity, fill_price)
        
        return {
            "order_id": order_id,
            "status": "FILLED",
            "filled_price": fill_price,
            "filled_qty": quantity
        }
    
    async def cancel_order(self, order_id: str) -> dict:
        """Cancel an order (fake implementation).
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        if order_id not in self.fake_orders:
            return {
                "order_id": order_id,
                "status": "NOT_FOUND",
                "message": f"Order {order_id} not found"
            }
        
        order = self.fake_orders[order_id]
        
        # Can only cancel if not filled yet (but all our fake orders are filled)
        if order["status"] == "FILLED":
            return {
                "order_id": order_id,
                "status": "ALREADY_FILLED",
                "message": "Cannot cancel filled order"
            }
        
        order["status"] = "CANCELLED"
        
        return {
            "order_id": order_id,
            "status": "CANCELLED"
        }
    
    async def get_active_positions(self) -> List[dict]:
        """Get all active positions.
        
        Returns:
            List of position dictionaries
        """
        return [
            pos for pos in self.fake_positions
            if pos.get("quantity", 0) != 0
        ]
    
    async def close_position(self, symbol: str) -> dict:
        """Close a position (fake implementation).
        
        Args:
            symbol: Symbol to close position for
            
        Returns:
            Close result dictionary
        """
        # Find position
        position = None
        for pos in self.fake_positions:
            if pos["symbol"] == symbol and pos.get("quantity", 0) != 0:
                position = pos
                break
        
        if not position:
            return {
                "symbol": symbol,
                "status": "NOT_FOUND",
                "message": f"No open position for {symbol}"
            }
        
        # Close by submitting opposite order
        close_side = "SELL" if position["side"] == "LONG" else "BUY"
        close_qty = abs(position["quantity"])
        
        result = await self.submit_order(
            symbol=symbol,
            side=close_side,
            quantity=close_qty,
            order_type="MARKET"
        )
        
        return {
            "symbol": symbol,
            "status": "CLOSED",
            "close_order_id": result["order_id"],
            "realized_pnl": self._calculate_pnl(position, result["filled_price"])
        }
    
    def _update_positions(self, symbol: str, side: str, quantity: float, price: float):
        """Update positions based on new order."""
        # Find existing position for this symbol
        existing = None
        for pos in self.fake_positions:
            if pos["symbol"] == symbol:
                existing = pos
                break
        
        if not existing:
            # Create new position
            self.fake_positions.append({
                "symbol": symbol,
                "side": "LONG" if side == "BUY" else "SHORT",
                "quantity": quantity if side == "BUY" else -quantity,
                "entry_price": price,
                "current_price": price,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0
            })
        else:
            # Update existing position
            if side == "BUY":
                existing["quantity"] += quantity
            else:
                existing["quantity"] -= quantity
            
            # Update average entry price
            # (Simplified - real implementation would be more complex)
            existing["entry_price"] = price
            existing["current_price"] = price
    
    def _calculate_pnl(self, position: dict, close_price: float) -> float:
        """Calculate realized PnL."""
        entry_price = position["entry_price"]
        quantity = abs(position["quantity"])
        
        if position["side"] == "LONG":
            return (close_price - entry_price) * quantity
        else:
            return (entry_price - close_price) * quantity
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds."""
        import time
        return int(time.time() * 1000)
    
    def get_order(self, order_id: str) -> Optional[dict]:
        """Get order details by ID."""
        return self.fake_orders.get(order_id)
    
    def get_all_orders(self) -> List[dict]:
        """Get all orders."""
        return list(self.fake_orders.values())
