"""Market Analysis Orchestrator - Main Agent.

Multi-agent market analysis system that:
1. Runs LangGraph-based analysis workflow with multiple analyst agents
2. Uses Trader AI to make final decisions
3. Dispatches to flexible execution backends
"""

from typing import Any, AsyncGenerator, Dict, Optional

from loguru import logger

from valuecell.core.agent.responses import streaming
from valuecell.core.types import BaseAgent, StreamResponse

from .config import get_default_backend, get_enabled_backends, get_llm_for_orchestrator
from .execution.backends.direct_order import DirectOrderBackend
from .execution.backends.grid_strategy import GridStrategyBackend
from .execution.backends.prompt_strategy import PromptStrategyBackend
from .execution.backends.quant_strategy import QuantStrategyBackend
from .execution.dispatcher import ExecutionDispatcher
from .internal_agents.trader.trader_ai import TraderAI


class MarketAnalysisOrchestrator(BaseAgent):
    """Multi-agent market analysis orchestrator.

    This agent orchestrates a team of analyst agents (market, fundamentals,
    news, social), researchers (bull/bear), risk debaters, and a Trader AI
    that makes final decisions and selects execution backends.

    Workflow:
    1. Parse query to extract symbol and parameters
    2. Run analysis workflow (analysts -> researchers -> risk -> trader)
    3. Trader AI selects execution backend based on conditions
    4. Dispatch to selected backend for execution
    5. Return comprehensive result

    Example query:
        "分析 000001.SZ 今天的投资价值并执行"
        "Analyze AAPL and recommend action"
    """

    def __init__(self, **kwargs):
        """Initialize the orchestrator."""
        super().__init__(**kwargs)

        # Initialize execution dispatcher
        self.dispatcher = ExecutionDispatcher()
        self._register_backends()

        # Initialize Trader AI
        llm = get_llm_for_orchestrator()
        self.trader = TraderAI(llm=llm, dispatcher=self.dispatcher)

        # Analysis graph will be initialized lazily
        self._graph = None

        logger.info("MarketAnalysisOrchestrator initialized")

    def _register_backends(self):
        """Register enabled execution backends."""
        enabled = get_enabled_backends()

        backend_map = {
            "direct_order": DirectOrderBackend,
            "prompt_strategy": PromptStrategyBackend,
            "quant_nautilus": QuantStrategyBackend,
            "grid_strategy": GridStrategyBackend,
        }

        for backend_id in enabled:
            if backend_id in backend_map:
                self.dispatcher.register_backend(backend_map[backend_id]())

        # Set default
        default = get_default_backend()
        if default in enabled:
            self.dispatcher.set_default_backend(default)

    async def stream(
        self,
        query: str,
        conversation_id: str,
        task_id: str,
        dependencies: Optional[Dict] = None,
    ) -> AsyncGenerator[StreamResponse, None]:
        """Stream the analysis and execution process.

        Args:
            query: User query (e.g., "分析 000001.SZ")
            conversation_id: Conversation ID
            task_id: Task ID
            dependencies: Optional dependencies

        Yields:
            StreamResponse events
        """
        logger.info(
            "MarketAnalysisOrchestrator.stream",
            query=query[:100],
            conversation_id=conversation_id,
        )

        # 1. Parse query
        yield streaming.message_chunk("📊 开始多智能体市场分析...\n")

        parsed = self._parse_query(query)
        symbol = parsed.get("symbol", "UNKNOWN")
        execute = parsed.get("execute", True)

        yield streaming.message_chunk(f"📈 分析标的: {symbol}\n")

        # 2. Run analysis workflow
        yield streaming.tool_call_started("analysis_workflow", "多智能体分析工作流")

        analysis_report = await self._run_analysis(symbol, query)
        risk_assessment = analysis_report.get("risk_assessment", {})

        yield streaming.tool_call_completed(
            f"分析完成，发现 {len(analysis_report)} 个分析维度",
            "analysis_workflow",
            "多智能体分析工作流",
        )

        # 3. Generate analysis summary
        yield streaming.message_chunk("\n## 分析摘要\n")
        for key, value in analysis_report.items():
            if key != "risk_assessment" and value:
                yield streaming.message_chunk(f"- **{key}**: {str(value)[:200]}\n")

        # 4. Trader AI decision
        if execute:
            yield streaming.message_chunk("\n🤖 **Trader AI 正在做出决策...**\n")

            decision = await self.trader.make_decision(
                analysis_report=analysis_report,
                risk_assessment=risk_assessment,
                market_context={"symbol": symbol},
            )

            yield streaming.message_chunk(
                f"\n### 交易决策\n"
                f"- **行动**: {decision.action}\n"
                f"- **执行后端**: {decision.backend_id}\n"
                f"- **理由**: {decision.rationale}\n"
            )

            # 5. Execute via backend
            yield streaming.tool_call_started(
                decision.backend_id, f"执行: {decision.backend_id}"
            )

            context = self.trader.get_decision_context(analysis_report, risk_assessment)
            result = await self.dispatcher.dispatch(decision, context)

            yield streaming.tool_call_completed(
                result.message, decision.backend_id, f"执行: {decision.backend_id}"
            )

            yield streaming.message_chunk(
                f"\n### 执行结果\n"
                f"- **成功**: {'✅' if result.success else '❌'}\n"
                f"- **消息**: {result.message}\n"
            )

            if result.trades:
                yield streaming.message_chunk(f"- **交易数量**: {len(result.trades)}\n")

        else:
            yield streaming.message_chunk("\n📋 仅分析模式，不执行交易\n")

        yield streaming.done()

    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract parameters.

        Args:
            query: User query string

        Returns:
            Dict with symbol, market_type, execute flags
        """
        import re

        result = {
            "symbol": "UNKNOWN",
            "market_type": "china",
            "execute": True,
        }

        # Extract stock code patterns
        # China A-shares: 000001.SZ, 600036.SH
        china_pattern = r"\b(\d{6}\.(SZ|SH|sz|sh))\b"
        china_match = re.search(china_pattern, query)
        if china_match:
            result["symbol"] = china_match.group(1).upper()
            result["market_type"] = "china"
            return result

        # Hong Kong: 0700.HK, 9988.HK
        hk_pattern = r"\b(\d{4,5}\.HK)\b"
        hk_match = re.search(hk_pattern, query, re.IGNORECASE)
        if hk_match:
            result["symbol"] = hk_match.group(1).upper()
            result["market_type"] = "hk"
            return result

        # US stocks: AAPL, GOOGL, etc.
        us_pattern = r"\b([A-Z]{1,5})\b"
        # Only match if it looks like someone is asking about a specific stock
        if any(kw in query.lower() for kw in ["analyze", "分析", "stock", "股票"]):
            us_match = re.search(us_pattern, query)
            if us_match:
                result["symbol"] = us_match.group(1)
                result["market_type"] = "us"
                return result

        # Check for analysis-only mode
        if any(kw in query.lower() for kw in ["仅分析", "只分析", "不执行", "analysis only"]):
            result["execute"] = False

        return result

    async def _run_analysis(self, symbol: str, query: str) -> Dict[str, Any]:
        """Run the multi-agent analysis workflow.

        Args:
            symbol: Stock symbol
            query: Original query

        Returns:
            Analysis report dictionary
        """
        # TODO: Implement full LangGraph workflow
        # For now, return placeholder analysis

        logger.info("Running analysis workflow", symbol=symbol)

        return {
            "market_analysis": f"市场技术分析: {symbol} 当前处于震荡区间",
            "fundamentals_analysis": f"基本面分析: {symbol} 财务状况良好，PE 合理",
            "news_analysis": "新闻分析: 暂无重大新闻事件",
            "social_analysis": "社交媒体分析: 市场情绪中性",
            "research_summary": "多空研究: 多方略占优势",
            "risk_assessment": {
                "risk_level": "medium",
                "aggressive_view": "可以适度加仓",
                "conservative_view": "建议观望",
                "neutral_view": "小仓位试探",
            },
            "recommendation": "hold",
            "confidence": 0.65,
        }
