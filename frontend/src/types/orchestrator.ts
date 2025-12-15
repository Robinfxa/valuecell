/**
 * Types for Market Analysis Orchestrator
 */

// Agent types in the orchestrator
export type OrchestratorAgentType =
    | "market_analyst"
    | "fundamentals_analyst"
    | "news_analyst"
    | "social_analyst"
    | "bull_researcher"
    | "bear_researcher"
    | "research_manager"
    | "risky_debater"
    | "safe_debater"
    | "neutral_debater"
    | "risk_manager"
    | "trader_ai";

// Prompt template structure
export interface PromptTemplate {
    id: string;
    name: string;
    agent_type: OrchestratorAgentType;
    content: string;
    variables: string[];
    description: string;
    is_default: boolean;
    created_at: string;
    updated_at: string;
}

// Template set for quick switching
export interface TemplateSet {
    id: string;
    name: string;
    description: string;
    template_ids: Record<OrchestratorAgentType, string>;
    is_default: boolean;
    created_at: string;
}

// Analysis request
export interface AnalysisRequest {
    query: string;
    ticker?: string;
    market_type?: "china" | "hk" | "us";
    trade_date?: string;
    selected_analysts?: OrchestratorAgentType[];
    template_set_id?: string;
}

// Agent output during analysis
export interface AgentOutput {
    agent_type: OrchestratorAgentType;
    agent_name: string;
    content: string;
    prompt_used?: string;
    timestamp: string;
    status: "pending" | "running" | "completed" | "error";
}

// Analysis progress
export interface AnalysisProgress {
    current_step: string;
    progress: number; // 0-100
    elapsed_time: number;
    estimated_remaining: number;
    agents_completed: string[];
    agents_pending: string[];
}

// Full analysis result
export interface AnalysisResult {
    id: string;
    ticker: string;
    trade_date: string;
    market_type: string;
    agent_outputs: Record<OrchestratorAgentType, AgentOutput>;
    final_decision: {
        action: "buy" | "sell" | "hold";
        confidence: number;
        target_price?: number;
        risk_level: "low" | "medium" | "high";
        reasoning: string;
    };
    created_at: string;
}

// Agent info for display
export interface OrchestratorAgentInfo {
    type: OrchestratorAgentType;
    display_name: string;
    description: string;
    icon: string;
    category: "analyst" | "researcher" | "risk" | "decision";
}

// All agent infos
export const ORCHESTRATOR_AGENTS: OrchestratorAgentInfo[] = [
    // Analysts
    {
        type: "market_analyst",
        display_name: "市场分析师",
        description: "技术分析和市场趋势",
        icon: "📊",
        category: "analyst",
    },
    {
        type: "fundamentals_analyst",
        display_name: "基本面分析师",
        description: "财务和估值分析",
        icon: "📈",
        category: "analyst",
    },
    {
        type: "news_analyst",
        display_name: "新闻分析师",
        description: "新闻和公告分析",
        icon: "📰",
        category: "analyst",
    },
    {
        type: "social_analyst",
        display_name: "社媒分析师",
        description: "社交媒体情绪",
        icon: "💬",
        category: "analyst",
    },
    // Researchers
    {
        type: "bull_researcher",
        display_name: "看涨研究员",
        description: "多方论证",
        icon: "🐂",
        category: "researcher",
    },
    {
        type: "bear_researcher",
        display_name: "看跌研究员",
        description: "空方论证",
        icon: "🐻",
        category: "researcher",
    },
    {
        type: "research_manager",
        display_name: "研究经理",
        description: "综合评估决策",
        icon: "👔",
        category: "researcher",
    },
    // Risk Management
    {
        type: "risky_debater",
        display_name: "激进分析师",
        description: "高风险高回报观点",
        icon: "🔥",
        category: "risk",
    },
    {
        type: "safe_debater",
        display_name: "保守分析师",
        description: "风险规避观点",
        icon: "🛡️",
        category: "risk",
    },
    {
        type: "neutral_debater",
        display_name: "中性分析师",
        description: "平衡观点",
        icon: "⚖️",
        category: "risk",
    },
    {
        type: "risk_manager",
        display_name: "风险经理",
        description: "最终风险决策",
        icon: "🎯",
        category: "risk",
    },
    // Decision
    {
        type: "trader_ai",
        display_name: "交易决策AI",
        description: "最终交易决策",
        icon: "🤖",
        category: "decision",
    },
];

export function getAgentInfo(
    type: OrchestratorAgentType
): OrchestratorAgentInfo | undefined {
    return ORCHESTRATOR_AGENTS.find((a) => a.type === type);
}
