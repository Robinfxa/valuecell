"""Simplified LangGraph-based analysis workflow.

This module provides a simplified version of the TradingAgents-CN
analysis graph, adapted to work within ValueCell's architecture.

The workflow follows this pattern:
1. Analysts (Market, Fundamentals, News, Social) analyze in parallel
2. Researchers (Bull, Bear) debate the findings
3. Research Manager summarizes
4. Risk Debaters evaluate risks
5. Trader AI makes final decision (handled externally)
"""

from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from loguru import logger

from ..internal_agents.states import AgentState, create_initial_state


class AnalysisGraph:
    """Simplified analysis workflow graph.

    This is a placeholder implementation that will be expanded
    to include full LangGraph integration in Phase 2.

    For now, it provides a basic structure that can be called
    from the main orchestrator.
    """

    def __init__(
        self,
        selected_analysts: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the analysis graph.

        Args:
            selected_analysts: List of analyst types to use
            config: Configuration dictionary
        """
        self.selected_analysts = selected_analysts or ["market", "fundamentals"]
        self.config = config or {}
        self._state: Optional[AgentState] = None

        logger.info(
            "AnalysisGraph initialized",
            selected_analysts=self.selected_analysts,
        )

    async def propagate(
        self,
        ticker: str,
        trade_date: str,
        market_type: str = "china",
    ) -> Dict[str, Any]:
        """Run the analysis workflow.

        Args:
            ticker: Stock symbol
            trade_date: Analysis date
            market_type: Market type (china/hk/us)

        Returns:
            Analysis results dictionary
        """
        logger.info(
            "Starting analysis propagation",
            ticker=ticker,
            date=trade_date,
            market=market_type,
        )

        # Initialize state
        self._state = create_initial_state(ticker, trade_date, market_type)

        # Run analysts (placeholder - returns mock data)
        await self._run_analysts()

        # Run researchers (placeholder)
        await self._run_researchers()

        # Run risk assessment (placeholder)
        await self._run_risk_assessment()

        return self.get_analysis_report()

    async def propagate_stream(
        self,
        ticker: str,
        trade_date: str,
        market_type: str = "china",
    ) -> AsyncIterator[Tuple[str, Dict[str, Any]]]:
        """Run the analysis workflow with streaming updates.

        Args:
            ticker: Stock symbol
            trade_date: Analysis date
            market_type: Market type

        Yields:
            Tuple of (node_name, output_dict) for each step
        """
        logger.info(
            "Starting streaming analysis",
            ticker=ticker,
            date=trade_date,
        )

        # Initialize state
        self._state = create_initial_state(ticker, trade_date, market_type)

        # Run analysts
        for analyst in self.selected_analysts:
            node_name = f"{analyst.capitalize()} Analyst"
            logger.debug(f"Running {node_name}")

            result = await self._run_single_analyst(analyst)
            yield node_name, {"report": result}

        # Run researchers
        yield "Bull Researcher", {"argument": await self._run_bull_researcher()}
        yield "Bear Researcher", {"argument": await self._run_bear_researcher()}
        yield "Research Manager", {"summary": await self._run_research_manager()}

        # Run risk assessment
        yield "Risk Debaters", {"assessment": await self._run_risk_assessment()}

    async def _run_analysts(self) -> None:
        """Run all selected analysts."""
        for analyst in self.selected_analysts:
            await self._run_single_analyst(analyst)

    async def _run_single_analyst(self, analyst_type: str) -> str:
        """Run a single analyst and update state.

        Args:
            analyst_type: Type of analyst (market, fundamentals, news, social)

        Returns:
            Analyst report string
        """
        ticker = self._state.get("company_of_interest", "UNKNOWN")
        date = self._state.get("trade_date", "")
        market_type = self._state.get("market_type", "china")

        # Get LLM from config (None = use placeholder)
        llm = self.config.get("llm")

        logger.debug(f"Running {analyst_type} analyst", ticker=ticker)

        try:
            # Import and create the appropriate analyst
            if analyst_type == "market":
                from ..internal_agents.analysts import create_market_analyst
                node_fn = create_market_analyst(llm=llm)
            elif analyst_type == "fundamentals":
                from ..internal_agents.analysts import create_fundamentals_analyst
                node_fn = create_fundamentals_analyst(llm=llm)
            elif analyst_type == "news":
                from ..internal_agents.analysts import create_news_analyst
                node_fn = create_news_analyst(llm=llm)
            elif analyst_type == "social":
                from ..internal_agents.analysts import create_social_analyst
                node_fn = create_social_analyst(llm=llm)
            else:
                return f"{analyst_type}分析完成"

            # Run the analyst node
            result = node_fn(self._state)

            # Handle report key mapping
            report_key = f"{analyst_type}_report"
            if analyst_type == "social":
                report_key = "sentiment_report"

            # Update state with the result
            if report_key in result:
                report = result[report_key]
                self._state[report_key] = report
                return report
            else:
                # Fallback to mock if no report returned
                report = f"{analyst_type}分析: {ticker} 分析完成"
                self._state[report_key] = report
                return report

        except Exception as e:
            logger.exception(f"Error running {analyst_type} analyst: {e}")
            report = f"{analyst_type}分析失败: {e}"
            report_key = f"{analyst_type}_report"
            if analyst_type == "social":
                report_key = "sentiment_report"
            self._state[report_key] = report
            return report


    async def _run_researchers(self) -> None:
        """Run bull and bear researchers."""
        await self._run_bull_researcher()
        await self._run_bear_researcher()
        await self._run_research_manager()

    async def _run_bull_researcher(self) -> str:
        """Run bull researcher."""
        return "多方观点: 技术面向好，建议适当加仓"

    async def _run_bear_researcher(self) -> str:
        """Run bear researcher."""
        return "空方观点: 市场存在不确定性，建议谨慎"

    async def _run_research_manager(self) -> str:
        """Run research manager to summarize."""
        summary = "综合研究: 多空双方意见后，建议持有观望"
        if self._state:
            self._state["investment_plan"] = summary
        return summary

    async def _run_risk_assessment(self) -> Dict[str, Any]:
        """Run risk assessment debate."""
        assessment = {
            "risk_level": "medium",
            "aggressive_view": "可以适度加仓，设好止损",
            "conservative_view": "建议观望等待更明确信号",
            "neutral_view": "小仓位试探，控制风险",
            "final_decision": "持有",
        }

        if self._state:
            self._state["final_trade_decision"] = assessment["final_decision"]

        return assessment

    def get_analysis_report(self) -> Dict[str, Any]:
        """Get the current analysis report.

        Returns:
            Dictionary containing all analysis results
        """
        if not self._state:
            return {}

        return {
            "market_analysis": self._state.get("market_report"),
            "fundamentals_analysis": self._state.get("fundamentals_report"),
            "news_analysis": self._state.get("news_report"),
            "social_analysis": self._state.get("sentiment_report"),
            "investment_plan": self._state.get("investment_plan"),
            "recommendation": self._state.get("final_trade_decision"),
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get the current risk assessment.

        Returns:
            Risk assessment dictionary
        """
        if not self._state:
            return {}

        return {
            "risk_level": "medium",
            "final_decision": self._state.get("final_trade_decision"),
        }
