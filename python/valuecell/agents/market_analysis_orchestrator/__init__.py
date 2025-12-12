"""Market Analysis Orchestrator Module.

Multi-agent market analysis system integrating:
- LangGraph-based multi-agent analysis workflow
- Flexible execution backend selection (Trader AI)
- Support for quantitative, prompt-based, and grid strategies
"""

from .core import MarketAnalysisOrchestrator

__all__ = ["MarketAnalysisOrchestrator"]
