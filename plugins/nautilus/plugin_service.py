"""Nautilus Plugin Service.

This module provides the main service interface for the Nautilus Plugin,
coordinating data adapters, execution wrappers, and strategy pools.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from valuecell.plugins.nautilus.data_adapter import NautilusDataAdapter
from valuecell.plugins.nautilus.execution_wrapper import NautilusExecutionWrapper
from valuecell.plugins.nautilus.strategy_pool import NautilusStrategyPool


@dataclass
class StartStrategyRequest:
    """Request to start a trading strategy."""
    
    strategy_id: str
    """Strategy ID from the strategy pool"""
    
    parameters: Dict[str, Any] = field(default_factory=dict)
    """Optional parameters to override strategy defaults"""
    
    symbols: List[str] = field(default_factory=list)
    """List of trading symbols (e.g., ["BTC/USDT"])"""
    
    mode: str = "backtest"
    """Execution mode: backtest | paper | live"""
    
    initial_capital: float = 10000.0
    """Initial capital for this strategy run"""


@dataclass
class StartStrategyResponse:
    """Response after starting a strategy."""
    
    run_id: str
    """Unique identifier for this strategy run"""
    
    status: str
    """Status: STARTED | FAILED"""
    
    message: str = ""
    """Human-readable status message"""
    
    error_code: Optional[str] = None
    """Error code if status is FAILED"""


@dataclass
class StopStrategyRequest:
    """Request to stop a running strategy."""
    
    run_id: str
    """Strategy run ID to stop"""
    
    force: bool = False
    """If True, force close all positions immediately"""


@dataclass
class StopStrategyResponse:
    """Response after stopping a strategy."""
    
    run_id: str
    """Strategy run ID"""
    
    status: str
    """Status: STOPPED | NOT_FOUND"""
    
    final_pnl: float = 0.0
    """Final realized PnL"""
    
    message: str = ""
    """Human-readable status message"""


@dataclass
class GetReportRequest:
    """Request to get strategy performance report."""
    
    run_id: str
    """Strategy run ID"""
    
    include_orders: bool = True
    """Whether to include order history"""
    
    include_positions: bool = True
    """Whether to include current positions"""


@dataclass
class PerformanceMetrics:
    """Performance metrics for a strategy run."""
    
    total_pnl: float = 0.0
    """Total realized + unrealized PnL"""
    
    total_return_pct: float = 0.0
    """Total return percentage"""
    
    sharpe_ratio: float = 0.0
    """Sharpe ratio (if calculable)"""
    
    max_drawdown: float = 0.0
    """Maximum drawdown percentage"""
    
    win_rate: float = 0.0
    """Win rate (winning trades / total trades)"""
    
    total_trades: int = 0
    """Total number of trades"""
    
    winning_trades: int = 0
    """Number of winning trades"""
    
    losing_trades: int = 0
    """Number of losing trades"""


@dataclass
class GetReportResponse:
    """Response containing strategy performance report."""
    
    run_id: str
    """Strategy run ID"""
    
    strategy_id: str
    """Strategy ID"""
    
    performance: PerformanceMetrics
    """Performance metrics"""
    
    current_positions: List[dict] = field(default_factory=list)
    """Current open positions"""
    
    recent_orders: List[dict] = field(default_factory=list)
    """Recent orders"""
    
    start_time: float = 0.0
    """Strategy start timestamp"""
    
    runtime_seconds: float = 0.0
    """Total runtime in seconds"""


class NautilusPlugin:
    """
    Nautilus Plugin Service.
    
    Main service class that coordinates all Nautilus components:
    - Data adapters for market data
    - Execution wrappers for order management
    - Strategy pool for strategy selection
    
    This provides a unified interface that ValueCell can interact with.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Nautilus Plugin.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.data_adapter = NautilusDataAdapter(self.config.get("data", {}))
        self.execution = NautilusExecutionWrapper(self.config.get("execution", {}))
        self.pool = NautilusStrategyPool()
        
        # Track active strategy runs
        self.active_runs: Dict[str, Dict[str, Any]] = {}
    
    async def start_strategy(
        self,
        request: StartStrategyRequest
    ) -> StartStrategyResponse:
        """Start a trading strategy.
        
        Args:
            request: Strategy start request
            
        Returns:
            Start response with run_id or error
        """
        try:
            # Generate unique run ID
            run_id = uuid.uuid4().hex
            
            # Validate strategy exists
            descriptor = self.pool.get_strategy_descriptor(request.strategy_id)
            if not descriptor:
                return StartStrategyResponse(
                    run_id="",
                    status="FAILED",
                    error_code="STRATEGY_NOT_FOUND",
                    message=f"Strategy '{request.strategy_id}' not found in pool"
                )
            
            # Create strategy instance
            strategy = self.pool.create_strategy_instance(
                request.strategy_id,
                request.parameters
            )
            
            # Start strategy
            strategy.start()
            
            # Subscribe to market data for each symbol
            subscription_ids = []
            for symbol in request.symbols:
                async def data_callback(data):
                    # In real implementation, feed data to strategy
                    pass
                
                sub_id = await self.data_adapter.subscribe_market_data(
                    symbol, "quote", data_callback
                )
                subscription_ids.append(sub_id)
            
            # Store run information
            self.active_runs[run_id] = {
                "strategy": strategy,
                "strategy_id": request.strategy_id,
                "symbols": request.symbols,
                "subscription_ids": subscription_ids,
                "start_time": time.time(),
                "initial_capital": request.initial_capital,
                "mode": request.mode
            }
            
            return StartStrategyResponse(
                run_id=run_id,
                status="STARTED",
                message=f"Strategy '{descriptor.name}' started successfully"
            )
            
        except Exception as e:
            return StartStrategyResponse(
                run_id="",
                status="FAILED",
                error_code="INTERNAL_ERROR",
                message=str(e)
            )
    
    async def stop_strategy(
        self,
        request: StopStrategyRequest
    ) -> StopStrategyResponse:
        """Stop a running strategy.
        
        Args:
            request: Strategy stop request
            
        Returns:
            Stop response with final status
        """
        if request.run_id not in self.active_runs:
            return StopStrategyResponse(
                run_id=request.run_id,
                status="NOT_FOUND",
                message=f"Run ID '{request.run_id}' not found"
            )
        
        run = self.active_runs[request.run_id]
        
        # Stop strategy
        strategy = run["strategy"]
        strategy.stop()
        
        # Unsubscribe from market data
        for sub_id in run["subscription_ids"]:
            await self.data_adapter.unsubscribe(sub_id)
        
        # If force, close all positions
        final_pnl = 0.0
        if request.force:
            positions = await self.execution.get_active_positions()
            for pos in positions:
                result = await self.execution.close_position(pos["symbol"])
                final_pnl += result.get("realized_pnl", 0.0)
        
        # Remove from active runs
        del self.active_runs[request.run_id]
        
        return StopStrategyResponse(
            run_id=request.run_id,
            status="STOPPED",
            final_pnl=final_pnl,
            message="Strategy stopped successfully"
        )
    
    async def get_report(
        self,
        request: GetReportRequest
    ) -> GetReportResponse:
        """Get performance report for a strategy run.
        
        Args:
            request: Report request
            
        Returns:
            Performance report
        """
        if request.run_id not in self.active_runs:
            # Return empty report for unknown run
            return GetReportResponse(
                run_id=request.run_id,
                strategy_id="unknown",
                performance=PerformanceMetrics()
            )
        
        run = self.active_runs[request.run_id]
        
        # Get current positions
        positions = []
        if request.include_positions:
            positions = await self.execution.get_active_positions()
        
        # Get orders
        orders = []
        if request.include_orders:
            orders = self.execution.get_all_orders()
        
        # Calculate runtime
        runtime = time.time() - run["start_time"]
        
        # Calculate basic metrics (simplified for MVP)
        total_pnl = sum(pos.get("unrealized_pnl", 0) for pos in positions)
        all_orders = self.execution.get_all_orders()
        
        performance = PerformanceMetrics(
            total_pnl=total_pnl,
            total_return_pct=(total_pnl / run["initial_capital"]) * 100 if run["initial_capital"] > 0 else 0,
            total_trades=len(all_orders),
            winning_trades=0,  # TODO: calculate from orders
            losing_trades=0
        )
        
        return GetReportResponse(
            run_id=request.run_id,
            strategy_id=run["strategy_id"],
            performance=performance,
            current_positions=positions,
            recent_orders=orders[-10:] if orders else [],  # Last 10 orders
            start_time=run["start_time"],
            runtime_seconds=runtime
        )
    
    def get_active_run_count(self) -> int:
        """Get number of currently active strategy runs."""
        return len(self.active_runs)
