"""Simple Backtest Engine for Signal-Based Strategies.

This module provides a lightweight backtesting engine that replays historical
data to test trading strategies without full Nautilus installation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
import time

from valuecell.plugins.nautilus.signals import TradingSignal, SignalAction
from valuecell.plugins.nautilus.light_strategy import LightStrategy


@dataclass
class Trade:
    """A completed trade."""
    entry_time: float
    exit_time: Optional[float] = None
    symbol: str = ""
    side: str = "LONG"  # LONG | SHORT
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    commission: float = 0.0
    
    def is_closed(self) -> bool:
        """Check if trade is closed."""
        return self.exit_time is not None


@dataclass
class Position:
    """Current position."""
    symbol: str
    side: str  # LONG | SHORT
    quantity: float
    entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    
    def update_price(self, price: float):
        """Update current price and unrealized PnL."""
        self.current_price = price
        if self.side == "LONG":
            self.unrealized_pnl = (price - self.entry_price) * self.quantity
        else:  # SHORT
            self.unrealized_pnl = (self.entry_price - price) * self.quantity


@dataclass
class BacktestResult:
    """Backtest results."""
    total_pnl: float = 0.0
    total_return_pct: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    start_capital: float = 0.0
    end_capital: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_pnl": self.total_pnl,
            "total_return_pct": self.total_return_pct,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown_pct,
            "sharpe_ratio": self.sharpe_ratio,
            "profit_factor": self.profit_factor,
            "start_capital": self.start_capital,
            "end_capital": self.end_capital,
        }


class SimpleBacktestEngine:
    """
    Simple backtest engine for signal-based strategies.
    
    Features:
    - Historical data replay
    - Signal execution simulation
    - PnL calculation
    - Performance metrics
    
    Example:
        >>> engine = SimpleBacktestEngine(
        ...     strategy=my_strategy,
        ...     initial_capital=10000.0,
        ...     commission=0.001  # 0.1%
        ... )
        >>> result = await engine.run(historical_data)
        >>> print(f"Total PnL: ${result.total_pnl:.2f}")
        >>> print(f"Win Rate: {result.win_rate:.1f}%")
    """
    
    def __init__(
        self,
        strategy: LightStrategy,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0001,    # 0.01%
    ):
        """Initialize backtest engine.
        
        Args:
            strategy: Strategy instance to test
            initial_capital: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # State
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        
        # Pending signals
        self.pending_signals: List[TradingSignal] = []
        
        # Connect strategy signal handler
        self.strategy.set_signal_handler(self._on_signal)
    
    def _on_signal(self, signal: TradingSignal):
        """Handle signal from strategy."""
        self.pending_signals.append(signal)
    
    async def run(self, data: pd.DataFrame) -> BacktestResult:
        """Run backtest on historical data.
        
        Args:
            data: Historical data DataFrame with columns:
                  - timestamp (or index)
                  - open, high, low, close, volume
                  - symbol (optional, default to first symbol)
                  
        Returns:
            Backtest results
        """
        print(f"🎯 Starting backtest...")
        print(f"   Initial capital: ${self.initial_capital:,.2f}")
        print(f"   Data points: {len(data)}")
        print()
        
        # Start strategy
        self.strategy.start()
        
        # Iterate through historical data
        for idx, row in data.iterrows():
            # Convert row to bar dict
            bar = self._row_to_bar(row)
            
            # Feed data to strategy
            self.strategy.on_bar(bar)
            
            # Process any pending signals
            self._process_signals(bar['close'], bar['timestamp'])
            
            # Update positions
            self._update_positions(bar['close'])
            
            # Record equity
            equity = self._calculate_equity()
            self.equity_curve.append(equity)
        
        # Stop strategy
        self.strategy.stop()
        
        # Calculate final results
        result = self._calculate_results()
        
        print(f"✅ Backtest complete!")
        print()
        
        return result
    
    def _row_to_bar(self, row) -> dict:
        """Convert DataFrame row to bar dict."""
        # Get symbol
        symbol = row.get('symbol', 'BTC/USDT')
        
        # Get timestamp
        if hasattr(row, 'name'):  # Index is timestamp
            timestamp = row.name
        else:
            timestamp = row.get('timestamp', time.time())
        
        return {
            'symbol': symbol,
            'open': float(row.get('open', row.get('close', 0))),
            'high': float(row.get('high', row.get('close', 0))),
            'low': float(row.get('low', row.get('close', 0))),
            'close': float(row['close']),
            'volume': float(row.get('volume', 0)),
            'timestamp': timestamp
        }
    
    def _process_signals(self, price: float, timestamp):
        """Process pending signals."""
        for signal in self.pending_signals:
            self._execute_signal(signal, price, timestamp)
        
        self.pending_signals.clear()
    
    def _execute_signal(self, signal: TradingSignal, price: float, timestamp):
        """Execute a trading signal.
        
        Args:
            signal: Trading signal
            price: Current price
            timestamp: Current timestamp
        """
        symbol = signal.symbol
        
        # Apply slippage
        if signal.action == SignalAction.BUY:
            execution_price = price * (1 + self.slippage)
        else:
            execution_price = price * (1 - self.slippage)
        
        # Calculate commission
        notional = signal.quantity * execution_price
        comm = notional * self.commission
        
        if signal.action == SignalAction.BUY:
            # Open long position
            if symbol in self.positions:
                # Add to existing position
                pos = self.positions[symbol]
                total_qty = pos.quantity + signal.quantity
                avg_price = (pos.entry_price * pos.quantity + execution_price * signal.quantity) / total_qty
                pos.quantity = total_qty
                pos.entry_price = avg_price
            else:
                # New position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side="LONG",
                    quantity=signal.quantity,
                    entry_price=execution_price,
                    current_price=execution_price
                )
            
            self.capital -= (notional + comm)
        
        elif signal.action == SignalAction.SELL:
            # Open short position (simplified: just close long)
            if symbol in self.positions:
                pos = self.positions[symbol]
                if pos.side == "LONG":
                    # Close position
                    pnl = (execution_price - pos.entry_price) * pos.quantity - comm
                    
                    # Record trade
                    self.trades.append(Trade(
                        entry_time=timestamp,
                        exit_time=timestamp,
                        symbol=symbol,
                        side="LONG",
                        entry_price=pos.entry_price,
                        exit_price=execution_price,
                        quantity=pos.quantity,
                        pnl=pnl,
                        pnl_pct=pnl / (pos.entry_price * pos.quantity) * 100,
                        commission=comm
                    ))
                    
                    self.capital += (notional - comm)
                    del self.positions[symbol]
        
        elif signal.action in [SignalAction.CLOSE_LONG, SignalAction.CLOSE_ALL]:
            # Close position
            if symbol in self.positions:
                pos = self.positions[symbol]
                notional = pos.quantity * execution_price
                pnl = (execution_price - pos.entry_price) * pos.quantity - comm
                
                # Record trade
                self.trades.append(Trade(
                    entry_time=timestamp,
                    exit_time=timestamp,
                    symbol=symbol,
                    side=pos.side,
                    entry_price=pos.entry_price,
                    exit_price=execution_price,
                    quantity=pos.quantity,
                    pnl=pnl,
                    pnl_pct=pnl / (pos.entry_price * pos.quantity) * 100,
                    commission=comm
                ))
                
                self.capital += (notional - comm)
                del self.positions[symbol]
    
    def _update_positions(self, price: float):
        """Update all positions with current price."""
        for pos in self.positions.values():
            pos.update_price(price)
    
    def _calculate_equity(self) -> float:
        """Calculate current total equity."""
        equity = self.capital
        for pos in self.positions.values():
            equity += pos.unrealized_pnl + (pos.entry_price * pos.quantity)
        return equity
    
    def _calculate_results(self) -> BacktestResult:
        """Calculate final backtest results."""
        result = BacktestResult()
        
        result.start_capital = self.initial_capital
        result.end_capital = self._calculate_equity()
        result.total_pnl = result.end_capital - result.start_capital
        result.total_return_pct = (result.total_pnl / result.start_capital) * 100
        
        result.trades = self.trades
        result.total_trades = len(self.trades)
        
        if result.total_trades > 0:
            wins = [t for t in self.trades if t.pnl > 0]
            losses = [t for t in self.trades if t.pnl < 0]
            
            result.winning_trades = len(wins)
            result.losing_trades = len(losses)
            result.win_rate = (result.winning_trades / result.total_trades) * 100
            
            if wins:
                result.avg_win = sum(t.pnl for t in wins) / len(wins)
            if losses:
                result.avg_loss = sum(t.pnl for t in losses) / len(losses)
            
            # Profit factor
            total_wins = sum(t.pnl for t in wins) if wins else 0
            total_losses = abs(sum(t.pnl for t in losses)) if losses else 0
            if total_losses > 0:
                result.profit_factor = total_wins / total_losses
        
        # Max drawdown
        result.equity_curve = self.equity_curve
        peak = self.equity_curve[0]
        max_dd = 0
        max_dd_pct = 0
        
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = peak - equity
            dd_pct = (dd / peak) * 100 if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        result.max_drawdown = max_dd
        result.max_drawdown_pct = max_dd_pct
        
        # Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = pd.Series(self.equity_curve).pct_change().dropna()
            if returns.std() > 0:
                result.sharpe_ratio = (returns.mean() / returns.std()) * (252 ** 0.5)  # Annualized
        
        return result
    
    def print_results(self, result: BacktestResult):
        """Print formatted results."""
        print("=" * 60)
        print("📊 BACKTEST RESULTS")
        print("=" * 60)
        print()
        print(f"Initial Capital:    ${result.start_capital:,.2f}")
        print(f"Final Capital:      ${result.end_capital:,.2f}")
        print(f"Total PnL:          ${result.total_pnl:,.2f}")
        print(f"Total Return:       {result.total_return_pct:.2f}%")
        print()
        print(f"Total Trades:       {result.total_trades}")
        print(f"Winning Trades:     {result.winning_trades}")
        print(f"Losing Trades:      {result.losing_trades}")
        print(f"Win Rate:           {result.win_rate:.1f}%")
        print()
        if result.avg_win > 0:
            print(f"Average Win:        ${result.avg_win:.2f}")
        if result.avg_loss < 0:
            print(f"Average Loss:       ${result.avg_loss:.2f}")
        if result.profit_factor > 0:
            print(f"Profit Factor:      {result.profit_factor:.2f}")
        print()
        print(f"Max Drawdown:       ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%)")
        if result.sharpe_ratio != 0:
            print(f"Sharpe Ratio:       {result.sharpe_ratio:.2f}")
        print()
        print("=" * 60)
