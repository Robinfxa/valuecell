"""Trader AI - Final Decision and Execution Backend Selection.

The Trader AI receives comprehensive analysis from the multi-agent
workflow and makes the final trading decision, including selecting
the most appropriate execution backend.
"""

import json
from typing import Any, Dict, Optional

from loguru import logger

from ...execution.backends.base import ExecutionDecision
from ...execution.dispatcher import ExecutionDispatcher


class TraderAI:
    """Trader AI - Chief Investment Officer of the multi-agent system.

    Responsibilities:
    1. Receive analysis reports from all analysts
    2. Consider risk assessments from debaters
    3. Make final trading decision (buy/sell/hold)
    4. Select the best execution backend based on market conditions
    5. Generate execution parameters

    The Trader AI uses an LLM to make informed decisions based on
    the comprehensive context provided by the analysis workflow.
    """

    def __init__(self, llm: Any, dispatcher: ExecutionDispatcher):
        """Initialize Trader AI.

        Args:
            llm: The LLM instance to use for decision making
            dispatcher: The execution dispatcher for backend selection
        """
        self.llm = llm
        self.dispatcher = dispatcher

    async def make_decision(
        self,
        analysis_report: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionDecision:
        """Make trading decision and select execution backend.

        Args:
            analysis_report: Comprehensive analysis from all agents
            risk_assessment: Risk evaluation from debaters
            market_context: Current market conditions

        Returns:
            ExecutionDecision with action, backend, and parameters
        """
        market_context = market_context or {}

        # Build decision prompt
        prompt = self._build_decision_prompt(
            analysis_report,
            risk_assessment,
            market_context,
        )

        logger.debug("TraderAI decision prompt built", prompt_length=len(prompt))

        try:
            # Call LLM for decision
            response = await self._call_llm(prompt)
            decision = self._parse_decision(response, market_context)

            logger.info(
                "TraderAI decision made",
                action=decision.action,
                backend=decision.backend_id,
                symbol=decision.symbol,
            )

            return decision

        except Exception as e:
            logger.exception("TraderAI decision failed", error=str(e))
            # Return safe default
            return ExecutionDecision(
                backend_id="direct_order",
                action="hold",
                symbol=market_context.get("symbol", "UNKNOWN"),
                rationale=f"Decision failed, defaulting to hold: {e}",
            )

    def _build_decision_prompt(
        self,
        analysis_report: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        market_context: Dict[str, Any],
    ) -> str:
        """Build the decision prompt for the LLM.

        Args:
            analysis_report: Analysis from all agents
            risk_assessment: Risk evaluation
            market_context: Current conditions

        Returns:
            Formatted prompt string
        """
        backends_prompt = self.dispatcher.get_backends_prompt()

        return f"""You are the Chief Investment Officer making the final trading decision.

## ANALYSIS REPORT
{json.dumps(analysis_report, indent=2, ensure_ascii=False, default=str)}

## RISK ASSESSMENT
{json.dumps(risk_assessment, indent=2, ensure_ascii=False, default=str)}

## CURRENT MARKET CONTEXT
{json.dumps(market_context, indent=2, ensure_ascii=False, default=str)}

## {backends_prompt}

## YOUR TASK
Based on the comprehensive analysis, decide:
1. What action to take (buy/sell/hold/delegate)
2. Which execution backend best fits the current situation
3. Specific parameters for the chosen backend

Guidelines for backend selection:
- If market is trending clearly → use "quant_nautilus" with appropriate strategy
- If situation is complex, needs nuanced judgment → use "prompt_strategy"
- If simple entry/exit → use "direct_order"
- If ranging market with clear bounds → use "grid_strategy"

Respond in JSON format ONLY:
{{
    "action": "buy|sell|hold|delegate",
    "backend_id": "backend_id",
    "symbol": "SYMBOL",
    "quantity": 0.0,
    "params": {{}},
    "rationale": "Explanation of decision and backend choice"
}}
"""

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the decision prompt.

        Args:
            prompt: The formatted prompt

        Returns:
            LLM response string
        """
        if self.llm is None:
            # Return default response if no LLM configured
            logger.warning("No LLM configured, returning default response")
            return json.dumps({
                "action": "hold",
                "backend_id": "direct_order",
                "symbol": "UNKNOWN",
                "quantity": 0,
                "params": {},
                "rationale": "No LLM configured, defaulting to hold",
            })

        # Call LLM (supports various LLM interfaces)
        if hasattr(self.llm, "ainvoke"):
            response = await self.llm.ainvoke(prompt)
            if hasattr(response, "content"):
                return response.content
            return str(response)
        elif hasattr(self.llm, "arun"):
            return await self.llm.arun(prompt)
        else:
            # Fallback for callable
            return self.llm(prompt)

    def _parse_decision(
        self, response: str, market_context: Dict[str, Any]
    ) -> ExecutionDecision:
        """Parse the LLM response into an ExecutionDecision.

        Args:
            response: LLM response string
            market_context: Context for fallback values

        Returns:
            Parsed ExecutionDecision
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            data = json.loads(json_str.strip())

            return ExecutionDecision(
                backend_id=data.get("backend_id", "direct_order"),
                action=data.get("action", "hold"),
                symbol=data.get("symbol", market_context.get("symbol", "UNKNOWN")),
                quantity=data.get("quantity"),
                params=data.get("params", {}),
                rationale=data.get("rationale", "No rationale provided"),
            )

        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse LLM response as JSON",
                error=str(e),
                response=response[:200],
            )
            return ExecutionDecision(
                backend_id="direct_order",
                action="hold",
                symbol=market_context.get("symbol", "UNKNOWN"),
                rationale=f"Failed to parse response: {response[:100]}",
            )

    def get_decision_context(
        self,
        analysis_report: Dict[str, Any],
        risk_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build context dictionary for execution.

        Args:
            analysis_report: Analysis results
            risk_assessment: Risk evaluation

        Returns:
            Combined context dictionary
        """
        return {
            "analysis_report": analysis_report,
            "risk_assessment": risk_assessment,
        }
