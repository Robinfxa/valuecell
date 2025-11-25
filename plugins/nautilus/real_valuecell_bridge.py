"""Real ValueCell Bridge Implementation.

This module provides a real bridge to ValueCell's trading system using
the Agent-to-Agent (A2A) protocol for live trading operations.

Note: This is a CONCEPTUAL implementation showing how to integrate with
ValueCell. Actual integration would require:
1. ValueCell server running
2. Proper API endpoints configured
3. Authentication credentials
4. Risk management setup
"""

import asyncio
from typing import Optional, Dict, Any
import httpx
import json
from datetime import datetime

from valuecell.plugins.nautilus.signals import TradingSignal, SignalResult, SignalAction
from valuecell.plugins.nautilus.execution_bridge import ExecutionBridge


class RealValueCellBridge(ExecutionBridge):
    """
    Real ValueCell execution bridge using A2A protocol.
    
    This connects Nautilus trading signals to ValueCell's actual
    trading infrastructure for live market operations.
    
    Architecture:
        Nautilus Strategy → Signal → RealValueCellBridge → ValueCell Agent → Exchange
    """
    
    def __init__(
        self,
        valuecell_url: str = "http://localhost:8000",
        agent_id: str = "nautilus_strategy_agent",
        api_key: Optional[str] = None,
        dry_run: bool = True
    ):
        """
        Initialize Real ValueCell Bridge.
        
        Args:
            valuecell_url: ValueCell backend URL
            agent_id: Agent identifier for A2A protocol
            api_key: Optional API key for authentication
            dry_run: If True, simulate orders (paper trading)
        """
        self.valuecell_url = valuecell_url.rstrip('/')
        self.agent_id = agent_id
        self.api_key = api_key
        self.dry_run = dry_run
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=30.0
        )
        
        # Track execution state
        self.orders = []
        self.positions = {}
        self._initialized = False
        
        print(f"🔗 RealValueCellBridge initialized:")
        print(f"   URL: {valuecell_url}")
        print(f"   Agent: {agent_id}")
        print(f"   Mode: {'DRY RUN (Paper)' if dry_run else 'LIVE TRADING ⚠️'}")
        print()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Nautilus-ValueCell-Bridge/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def initialize(self) -> bool:
        """
        Initialize connection to ValueCell.
        
        Returns:
            True if connection successful
        """
        if self._initialized:
            return True
        
        try:
            # Check ValueCell health
            response = await self.client.get(f"{self.valuecell_url}/health")
            
            if response.status_code == 200:
                print("✅ Connected to ValueCell backend")
                self._initialized = True
                return True
            else:
                print(f"⚠️  ValueCell returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to ValueCell: {e}")
            print(f"   Make sure ValueCell is running at {self.valuecell_url}")
            return False
    
    async def execute_signal(self, signal: TradingSignal) -> SignalResult:
        """
        Execute trading signal through ValueCell.
        
        Args:
            signal: Trading signal from strategy
            
        Returns:
            Execution result
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert signal to ValueCell order format
            order_params = self._signal_to_order(signal)
            
            if self.dry_run:
                # Paper trading mode
                return await self._execute_paper_order(signal, order_params)
            else:
                # Live trading mode
                return await self._execute_live_order(signal, order_params)
                
        except Exception as e:
            return SignalResult(
                signal_id=signal.signal_id,
                success=False,
                error_message=f"Execution failed: {str(e)}"
            )
    
    async def get_position(self, symbol: str) -> Optional[dict]:
        """
        Get current position from ValueCell.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position dict or None
        """
        try:
            response = await self.client.get(
                f"{self.valuecell_url}/api/positions/{symbol}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Failed to get position: {e}")
            return None
    
    def _signal_to_order(self, signal: TradingSignal) -> Dict[str, Any]:
        """
        Convert Nautilus signal to ValueCell order format.
        
        Args:
            signal: Trading signal
            
        Returns:
            Order parameters dict
        """
        # Determine order side
        if signal.action == SignalAction.BUY:
            side = "buy"
        elif signal.action == SignalAction.SELL:
            side = "sell"
        elif signal.action == SignalAction.CLOSE_ALL:
            side = "close"
        else:
            side = "unknown"
        
        # Build order params
        order = {
            "symbol": signal.symbol,
            "side": side,
            "quantity": signal.quantity,
            "order_type": signal.order_type,
            "price": signal.price,
            "metadata": {
                "signal_id": signal.signal_id,
                "strategy_id": signal.strategy_id,
                "reason": signal.reason,
                "timestamp": signal.timestamp
            }
        }
        
        return order
    
    async def _execute_paper_order(
        self,
        signal: TradingSignal,
        order_params: Dict[str, Any]
    ) -> SignalResult:
        """
        Execute order in paper trading mode (simulation).
        
        Args:
            signal: Original signal
            order_params: Order parameters
            
        Returns:
            Simulated execution result
        """
        # Simulate order execution
        order_id = f"paper_{len(self.orders):04d}"
        
        # Create order record
        order = {
            "order_id": order_id,
            "status": "FILLED",
            "signal_id": signal.signal_id,
            "params": order_params,
            "filled_at": datetime.now().isoformat(),
            "mode": "PAPER"
        }
       
        self.orders.append(order)
        
        print(f"📝 Paper Order Executed:")
        print(f"   Order ID: {order_id}")
        print(f"   {order_params['side'].upper()} {order_params['quantity']} {order_params['symbol']}")
        print(f"   Reason: {signal.reason}")
        
        return SignalResult(
            signal_id=signal.signal_id,
            success=True,
            order_id=order_id,
            metadata={"mode": "paper", "order": order}
        )
    
    async def _execute_live_order(
        self,
        signal: TradingSignal,
        order_params: Dict[str, Any]
    ) -> SignalResult:
        """
        Execute order in live trading mode.
        
        WARNING: This executes real orders on real exchanges!
        
        Args:
            signal: Original signal
            order_params: Order parameters
            
        Returns:
            Live execution result
        """
        try:
            # Send order to ValueCell
            response = await self.client.post(
                f"{self.valuecell_url}/api/orders",
                json=order_params
            )
            
            if response.status_code == 200:
                result = response.json()
                order_id = result.get("order_id")
                
                print(f"✅ Live Order Executed:")
                print(f"   Order ID: {order_id}")
                print(f"   {order_params['side'].upper()} {order_params['quantity']} {order_params['symbol']}")
                
                return SignalResult(
                    signal_id=signal.signal_id,
                    success=True,
                    order_id=order_id,
                    metadata={"mode": "live", "response": result}
                )
            else:
                error_msg = f"ValueCell returned {response.status_code}: {response.text}"
                print(f"❌ Live Order Failed: {error_msg}")
                
                return SignalResult(
                    signal_id=signal.signal_id,
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            error_msg = f"Live execution error: {str(e)}"
            print(f"❌ {error_msg}")
            
            return SignalResult(
                signal_id=signal.signal_id,
                success=False,
                error_message=error_msg
            )
    
    async def close(self):
        """Close the bridge and cleanup resources."""
        await self.client.aclose()
        print("🔒 RealValueCellBridge closed")
    
    def get_order_history(self) -> list:
        """Get all executed orders."""
        return self.orders
    
    def get_execution_stats(self) -> dict:
        """Get execution statistics."""
        total = len(self.orders)
        filled = sum(1 for o in self.orders if o.get("status") == "FILLED")
        
        return {
            "total_orders": total,
            "filled_orders": filled,
            "mode": "PAPER" if self.dry_run else "LIVE",
            "agent_id": self.agent_id
        }


# Example usage and testing
async def example_usage():
    """Demonstrate RealValueCellBridge usage."""
    print()
    print("=" * 70)
    print("🎯 RealValueCellBridge Example")
    print("=" * 70)
    print()
    
    # Create bridge (paper trading mode)
    bridge = RealValueCellBridge(
        valuecell_url="http://localhost:8000",
        agent_id="nautilus_strategy_agent",
        dry_run=True  # Paper trading
    )
    
    # Initialize connection
    connected = await bridge.initialize()
    
    if not connected:
        print("⚠️  Could not connect to ValueCell")
        print("   This is expected if ValueCell is not running")
        print("   Bridge will work in offline paper mode")
        print()
    
    # Create a test signal
    from valuecell.plugins.nautilus.signals import TradingSignal, SignalType
    
    test_signal = TradingSignal(
        signal_id="test_001",
        strategy_id="example_strategy",
        signal_type=SignalType.ENTRY,
        action=SignalAction.BUY,
        symbol="BTC/USDT",
        quantity=0.01,
        price=50000.0,
        reason="Test signal for demonstration"
    )
    
    # Execute signal
    result = await bridge.execute_signal(test_signal)
    
    print()
    print("📊 Execution Result:")
    print(f"   Success: {result.success}")
    print(f"   Order ID: {result.order_id}")
    print()
    
    # Get stats
    stats = bridge.get_execution_stats()
    print("📈 Execution Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Cleanup
    await bridge.close()
    
    print("=" * 70)
    print("✅ Example Complete")
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(example_usage())
