"""State definitions for internal agents.

These TypedDicts define the state that flows through the LangGraph
multi-agent workflow.
"""

from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """Main agent state shared across the analysis workflow.

    This state accumulates results from all analyst agents and
    flows through researchers, risk managers, and the trader.
    """

    # Input parameters
    ticker: str
    trade_date: str
    market_type: str  # "china", "hk", "us"

    # Analyst outputs
    market_analysis: Optional[str]
    fundamentals_analysis: Optional[str]
    news_analysis: Optional[str]
    social_analysis: Optional[str]

    # Research outputs
    bull_argument: Optional[str]
    bear_argument: Optional[str]
    research_summary: Optional[str]

    # Risk assessment outputs
    aggressive_view: Optional[str]
    conservative_view: Optional[str]
    neutral_view: Optional[str]
    risk_decision: Optional[str]

    # Final decision
    final_decision: Optional[str]
    confidence: Optional[float]

    # Metadata
    messages: List[Dict[str, Any]]
    current_node: Optional[str]
    error: Optional[str]


class InvestDebateState(TypedDict, total=False):
    """State for the investment research debate.

    Used during the bull/bear researcher debate phase.
    """

    # Input from analysts
    market_info: Dict[str, Any]
    fundamentals_info: Dict[str, Any]
    news_info: Dict[str, Any]
    social_info: Dict[str, Any]

    # Debate outputs
    bull_argument: str
    bear_argument: str
    research_summary: str

    # Metadata
    debate_rounds: int
    current_speaker: str


class RiskDebateState(TypedDict, total=False):
    """State for the risk assessment debate.

    Used during the aggressive/conservative/neutral debater phase.
    """

    # Input from research
    research_summary: str
    market_context: Dict[str, Any]

    # Debate outputs
    aggressive_view: str
    conservative_view: str
    neutral_view: str
    risk_decision: str

    # Risk metrics
    risk_level: str  # "low", "medium", "high"
    position_size_recommendation: float
    stop_loss_recommendation: Optional[float]

    # Metadata
    debate_rounds: int
