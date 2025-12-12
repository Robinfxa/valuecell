"""Configuration adapter for Market Analysis Orchestrator.

Bridges the ValueCell configuration system with the orchestrator module.
"""

from typing import Any, Dict, List, Optional

from loguru import logger


def get_orchestrator_config() -> Dict[str, Any]:
    """Get orchestrator configuration from ValueCell config system.

    Returns:
        Configuration dictionary
    """
    try:
        from valuecell.config.loader import ConfigLoader

        loader = ConfigLoader()
        return loader.load_agent_config("market_analysis_orchestrator") or {}
    except Exception as e:
        logger.warning(f"Failed to load orchestrator config: {e}")
        return {}


def get_enabled_analysts() -> List[str]:
    """Get list of enabled analyst types.

    Returns:
        List of analyst identifiers (e.g., ["market", "fundamentals"])
    """
    config = get_orchestrator_config()
    analysts_config = config.get("analysts", {})
    return analysts_config.get("enabled", ["market", "fundamentals"])


def get_enabled_backends() -> List[str]:
    """Get list of enabled execution backends.

    Returns:
        List of backend IDs
    """
    config = get_orchestrator_config()
    execution_config = config.get("execution", {})
    return execution_config.get(
        "enabled_backends",
        ["direct_order", "prompt_strategy", "quant_nautilus", "grid_strategy"],
    )


def get_default_backend() -> str:
    """Get the default execution backend.

    Returns:
        Default backend ID
    """
    config = get_orchestrator_config()
    execution_config = config.get("execution", {})
    return execution_config.get("default_backend", "prompt_strategy")


def get_llm_for_orchestrator() -> Optional[Any]:
    """Get LLM instance for the orchestrator.

    Returns:
        LLM instance or None
    """
    try:
        from valuecell.utils.model import get_model

        return get_model("MARKET_ANALYSIS_MODEL_ID")
    except Exception as e:
        logger.warning(f"Failed to get LLM for orchestrator: {e}")

        # Try fallback to default model
        try:
            from valuecell.utils.model import get_model

            return get_model()
        except Exception:
            return None


def get_data_sources() -> Dict[str, List[str]]:
    """Get configured data sources by market.

    Returns:
        Dict mapping market type to list of data source names
    """
    config = get_orchestrator_config()
    return config.get(
        "data_sources",
        {
            "china": ["akshare"],
            "hk": ["yfinance"],
            "us": ["yfinance"],
        },
    )
