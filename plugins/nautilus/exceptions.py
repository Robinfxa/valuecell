"""Custom exceptions for Nautilus Plugin.

Defines specific exception types for better error handling and debugging.
"""


class NautilusPluginError(Exception):
    """Base exception for Nautilus plugin errors."""
    pass


class StrategyNotFoundError(NautilusPluginError):
    """Raised when a strategy is not found in the pool."""
    pass


class StrategyConfigurationError(NautilusPluginError):
    """Raised when strategy configuration is invalid."""
    pass


class DataFetchError(NautilusPluginError):
    """Raised when market data fetch fails."""
    pass


class ExecutionError(NautilusPluginError):
    """Raised when order execution fails."""
    pass


class ConnectionError(NautilusPluginError):
    """Raised when connection to ValueCell fails."""
    pass


class ValidationError(NautilusPluginError):
    """Raised when input validation fails."""
    pass
