"""Nautilus Hybrid Agent entry point."""

import asyncio
from valuecell.core.agent import create_wrapped_agent
from .core import NautilusHybridAgent


if __name__ == "__main__":
    agent = create_wrapped_agent(NautilusHybridAgent)
    asyncio.run(agent.serve())
