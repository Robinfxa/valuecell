"""State definitions for internal agents.

These TypedDicts define the state that flows through the LangGraph
multi-agent workflow. Adapted from TradingAgents-CN agent_states.py.
"""

from typing import Annotated, Any, Dict, List, Optional, Sequence

from typing_extensions import TypedDict


# Note: Using Dict instead of BaseMessage to avoid langchain dependency
# When LangGraph is fully integrated, this can be changed to BaseMessage
Message = Dict[str, Any]


def add_messages(left: List[Message], right: List[Message]) -> List[Message]:
    """Merge message lists, used as reducer for messages field."""
    return left + right


class InvestDebateState(TypedDict, total=False):
    """State for the investment research debate.

    Used during the bull/bear researcher debate phase.
    """

    bull_history: str  # Bullish argument history
    bear_history: str  # Bearish argument history
    history: str  # Combined conversation history
    current_response: str  # Latest response
    judge_decision: str  # Final judge decision
    count: int  # Debate round count


class RiskDebateState(TypedDict, total=False):
    """State for the risk assessment debate.

    Used during the aggressive/conservative/neutral debater phase.
    """

    risky_history: str  # Aggressive analyst history
    safe_history: str  # Conservative analyst history
    neutral_history: str  # Neutral analyst history
    history: str  # Combined conversation history
    latest_speaker: str  # Who spoke last
    current_risky_response: str  # Latest aggressive response
    current_safe_response: str  # Latest conservative response
    current_neutral_response: str  # Latest neutral response
    judge_decision: str  # Risk manager decision
    count: int  # Debate round count


class AgentState(TypedDict, total=False):
    """Main agent state shared across the analysis workflow.

    This state accumulates results from all analyst agents and
    flows through researchers, risk managers, and the trader.

    Adapted from TradingAgents-CN to work with ValueCell.
    """

    # Message history (for LangGraph MessagesState compatibility)
    messages: Annotated[Sequence[Message], add_messages]

    # Input parameters
    company_of_interest: str  # Stock symbol/ticker
    trade_date: str  # Analysis date
    market_type: str  # "china", "hk", "us"

    # Sender tracking
    sender: str  # Agent that sent this message

    # Analyst outputs (report strings)
    market_report: Optional[str]
    sentiment_report: Optional[str]  # Social media analysis
    news_report: Optional[str]
    fundamentals_report: Optional[str]

    # Tool call counters (for loop prevention)
    market_tool_call_count: int
    news_tool_call_count: int
    sentiment_tool_call_count: int
    fundamentals_tool_call_count: int

    # Research debate state
    investment_debate_state: Optional[InvestDebateState]
    investment_plan: Optional[str]

    # Trader output
    trader_investment_plan: Optional[str]

    # Risk debate state
    risk_debate_state: Optional[RiskDebateState]
    final_trade_decision: Optional[str]

    # Metadata
    current_node: Optional[str]
    error: Optional[str]


def create_initial_state(
    ticker: str,
    trade_date: str,
    market_type: str = "china",
) -> AgentState:
    """Create initial state for analysis workflow.

    Args:
        ticker: Stock symbol
        trade_date: Analysis date
        market_type: Market type (china/hk/us)

    Returns:
        Initialized AgentState
    """
    return AgentState(
        messages=[],
        company_of_interest=ticker,
        trade_date=trade_date,
        market_type=market_type,
        sender="",
        market_report=None,
        sentiment_report=None,
        news_report=None,
        fundamentals_report=None,
        market_tool_call_count=0,
        news_tool_call_count=0,
        sentiment_tool_call_count=0,
        fundamentals_tool_call_count=0,
        investment_debate_state=None,
        investment_plan=None,
        trader_investment_plan=None,
        risk_debate_state=None,
        final_trade_decision=None,
        current_node=None,
        error=None,
    )
