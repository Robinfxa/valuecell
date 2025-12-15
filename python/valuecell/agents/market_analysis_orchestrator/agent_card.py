"""A2A Protocol Agent Card for Market Analysis Orchestrator.

This module defines the Agent Card following the A2A (Agent-to-Agent) Protocol
specification v1.0. The Agent Card is a JSON document that acts as a digital
"business card" for this agent, used for discovery and initial interaction setup.

Reference: https://a2a-protocol.org/dev/
"""

from typing import Any, Dict, List

# A2A Protocol Agent Card Definition
AGENT_CARD: Dict[str, Any] = {
    # Required fields
    "protocolVersion": "1.0",
    "name": "Market Analysis Orchestrator",
    "description": (
        "智能多代理市场分析系统。整合技术分析、基本面分析、新闻分析和情绪分析，"
        "通过看涨/看跌研究员辩论和风险评估委员会，提供全面的投资决策支持。"
    ),
    "version": "1.0.0",
    
    # Capabilities
    "capabilities": {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True,
        "extensions": [],
    },
    
    # Default input/output modes
    "defaultInputModes": ["text/plain", "application/json"],
    "defaultOutputModes": ["text/plain", "application/json", "text/markdown"],
    
    # Provider information
    "provider": {
        "organization": "ValueCell",
        "url": "https://valuecell.io",
    },
    
    # Skills - A2A AgentSkill objects
    "skills": [
        {
            "id": "market-analysis",
            "name": "市场技术分析",
            "description": (
                "使用移动平均线、MACD、RSI、布林带等技术指标分析股票价格走势，"
                "识别买卖信号和趋势方向。"
            ),
            "tags": ["technical-analysis", "stock", "trading", "indicators"],
            "examples": [
                "分析贵州茅台(600519)的技术指标",
                "TSLA的MACD和RSI分析",
                "分析腾讯控股(0700.HK)的均线系统",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown", "application/json"],
        },
        {
            "id": "fundamentals-analysis",
            "name": "基本面分析",
            "description": (
                "分析公司财务数据、估值指标（PE/PB/PEG）、盈利能力和成长性，"
                "提供合理价位区间和投资评级。"
            ),
            "tags": ["fundamental-analysis", "valuation", "financials", "earnings"],
            "examples": [
                "分析宁德时代(300750)的基本面",
                "NVDA的估值分析",
                "比亚迪(1211.HK)的财务健康状况",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown", "application/json"],
        },
        {
            "id": "news-analysis",
            "name": "新闻分析",
            "description": (
                "分析公司相关新闻、行业动态和宏观环境变化，"
                "评估新闻对股价的短期和长期影响。"
            ),
            "tags": ["news", "sentiment", "current-events", "macro"],
            "examples": [
                "分析最新的茅台相关新闻",
                "苹果公司的最新公告影响分析",
                "小米集团的行业新闻分析",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown"],
        },
        {
            "id": "sentiment-analysis",
            "name": "社媒情绪分析",
            "description": (
                "分析社交媒体讨论热度、投资者情绪指标、"
                "KOL观点和论坛讨论倾向，识别情绪极端信号。"
            ),
            "tags": ["social-media", "sentiment", "investor-mood", "crowd"],
            "examples": [
                "分析雪球上关于中国平安的讨论",
                "特斯拉的Twitter情绪分析",
                "股吧里对招商银行的情绪倾向",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown"],
        },
        {
            "id": "investment-debate",
            "name": "投资辩论",
            "description": (
                "组织看涨和看跌研究员进行结构化辩论，"
                "综合分析增长潜力、风险因素和估值问题。"
            ),
            "tags": ["debate", "bull", "bear", "research"],
            "examples": [
                "对茅台进行多空辩论分析",
                "组织一场关于英伟达投资价值的辩论",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown"],
        },
        {
            "id": "risk-assessment",
            "name": "风险评估",
            "description": (
                "通过激进、保守和中性三方风险分析师的辩论，"
                "综合评估投资风险并提供仓位建议。"
            ),
            "tags": ["risk", "position-sizing", "stop-loss", "money-management"],
            "examples": [
                "评估投资贵州茅台的风险等级",
                "给出特斯拉的仓位建议",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["text/markdown", "application/json"],
        },
        {
            "id": "trading-decision",
            "name": "交易决策",
            "description": (
                "综合所有分析结果，生成最终的交易建议，"
                "包括具体的目标价位、止损位和置信度评分。"
            ),
            "tags": ["trading", "decision", "buy-sell", "target-price"],
            "examples": [
                "给出茅台的最终交易建议",
                "综合分析后，对苹果股票的投资决策",
            ],
            "inputModes": ["text/plain"],
            "outputModes": ["application/json", "text/markdown"],
        },
        {
            "id": "full-analysis",
            "name": "完整分析",
            "description": (
                "执行完整的多代理分析流程：技术分析、基本面分析、新闻分析、"
                "情绪分析、投资辩论、风险评估，最终生成综合投资报告。"
            ),
            "tags": ["comprehensive", "full-workflow", "investment-report"],
            "examples": [
                "对贵州茅台(600519)进行完整的投资分析",
                "全面分析NVDA的投资价值",
                "为腾讯控股生成完整投资报告",
            ],
            "inputModes": ["text/plain", "application/json"],
            "outputModes": ["text/markdown", "application/json"],
        },
    ],
    
    # Supports extended agent card (authenticated)
    "supportsExtendedAgentCard": False,
}


def get_agent_card() -> Dict[str, Any]:
    """Get the Agent Card for this orchestrator.
    
    Returns:
        A2A-compliant Agent Card dictionary
    """
    return AGENT_CARD.copy()


def get_agent_card_json() -> str:
    """Get the Agent Card as a JSON string.
    
    Returns:
        JSON-formatted Agent Card string
    """
    import json
    return json.dumps(AGENT_CARD, indent=2, ensure_ascii=False)
