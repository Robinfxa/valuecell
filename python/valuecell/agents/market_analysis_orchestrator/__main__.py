"""Entry point for running Market Analysis Orchestrator as a standalone agent."""

import asyncio

from valuecell.core.agent.decorator import create_wrapped_agent

from .core import MarketAnalysisOrchestrator

if __name__ == "__main__":
    agent = create_wrapped_agent(MarketAnalysisOrchestrator)
    asyncio.run(agent.serve())
