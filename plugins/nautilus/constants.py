"""Configuration constants for Nautilus Plugin.

Centralized constants for network, trading, and system configuration.
"""

from dataclasses import dataclass


# Network Configuration
DEFAULT_HTTP_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Trading Configuration
DEFAULT_COMMISSION_RATE = 0.001  # 0.1%
DEFAULT_SLIPPAGE_RATE = 0.0005   # 0.05%
DEFAULT_INITIAL_CAPITAL = 10000.0

# Position Sizing
MAX_POSITION_SIZE_PCT = 0.1  # 10% of capital
MIN_ORDER_SIZE = 0.001

# Backtest Configuration
DEFAULT_WARMUP_BARS = 50
MAX_BARS_IN_MEMORY = 10000

# Logging Configuration
LOG_ROTATION = "1 day"
LOG_RETENTION = "7 days"
LOG_LEVEL = "INFO"

# Agent Configuration
DEFAULT_AGENT_ID = "nautilus_strategy_agent"
DEFAULT_VALUECELL_URL = "http://localhost:8000"


@dataclass
class NetworkConfig:
    """Network configuration parameters."""
    http_timeout: float = DEFAULT_HTTP_TIMEOUT
    max_retries: int = MAX_RETRIES
    retry_delay: float = RETRY_DELAY


@dataclass
class TradingConfig:
    """Trading configuration parameters."""
    commission_rate: float = DEFAULT_COMMISSION_RATE
    slippage_rate: float = DEFAULT_SLIPPAGE_RATE
    initial_capital: float = DEFAULT_INITIAL_CAPITAL
    max_position_size_pct: float = MAX_POSITION_SIZE_PCT
    min_order_size: float = MIN_ORDER_SIZE


@dataclass
class BacktestConfig:
    """Backtest configuration parameters."""
    warmup_bars: int = DEFAULT_WARMUP_BARS
    max_bars_in_memory: int = MAX_BARS_IN_MEMORY
