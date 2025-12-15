import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
    ORCHESTRATOR_AGENTS,
    type OrchestratorAgentType,
    type AgentOutput,
} from "@/types/orchestrator";

// Mock data for demonstration - will be replaced with real API data
const MOCK_OUTPUTS: Partial<Record<OrchestratorAgentType, AgentOutput>> = {
    market_analyst: {
        agent_type: "market_analyst",
        agent_name: "市场分析师",
        content: "## 技术分析报告\n\n### 趋势分析\n- 短期趋势：上涨\n- MA5: 25.30 > MA10: 24.80\n- MACD 金叉形成\n\n### 建议\n技术面看多",
        timestamp: new Date().toISOString(),
        status: "completed",
        prompt_used: "你是一位专业的股票技术分析师...",
    },
    fundamentals_analyst: {
        agent_type: "fundamentals_analyst",
        agent_name: "基本面分析师",
        content: "## 基本面分析\n\n### 估值指标\n- PE: 18.5\n- PB: 2.8\n- ROE: 15.2%\n\n### 建议\n估值合理",
        timestamp: new Date().toISOString(),
        status: "completed",
    },
};

export function AgentOutputTabs() {
    const [activeAgent, setActiveAgent] =
        useState<OrchestratorAgentType>("market_analyst");

    const categories = {
        analyst: ORCHESTRATOR_AGENTS.filter((a) => a.category === "analyst"),
        researcher: ORCHESTRATOR_AGENTS.filter((a) => a.category === "researcher"),
        risk: ORCHESTRATOR_AGENTS.filter((a) => a.category === "risk"),
        decision: ORCHESTRATOR_AGENTS.filter((a) => a.category === "decision"),
    };

    const currentOutput = MOCK_OUTPUTS[activeAgent];

    return (
        <div className="grid grid-cols-4 gap-4">
            {/* Agent List Sidebar */}
            <Card className="col-span-1">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Agent 列表</CardTitle>
                </CardHeader>
                <CardContent className="p-2">
                    <div className="h-[500px] overflow-auto">
                        {Object.entries(categories).map(([category, agents]) => (
                            <div key={category} className="mb-4">
                                <div className="mb-2 px-2 text-xs font-medium uppercase text-muted-foreground">
                                    {category === "analyst" && "分析师"}
                                    {category === "researcher" && "研究员"}
                                    {category === "risk" && "风险管理"}
                                    {category === "decision" && "决策"}
                                </div>
                                <div className="space-y-1">
                                    {agents.map((agent) => {
                                        const hasOutput = !!MOCK_OUTPUTS[agent.type];
                                        return (
                                            <button
                                                key={agent.type}
                                                type="button"
                                                className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors ${activeAgent === agent.type
                                                        ? "bg-primary text-primary-foreground"
                                                        : "hover:bg-muted"
                                                    }`}
                                                onClick={() => setActiveAgent(agent.type)}
                                            >
                                                <span>{agent.icon}</span>
                                                <span className="flex-1 truncate">
                                                    {agent.display_name}
                                                </span>
                                                {hasOutput && (
                                                    <Badge variant="secondary" className="h-5 text-xs">
                                                        ✓
                                                    </Badge>
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Output Content */}
            <Card className="col-span-3">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                            {ORCHESTRATOR_AGENTS.find((a) => a.type === activeAgent)?.icon}
                            {
                                ORCHESTRATOR_AGENTS.find((a) => a.type === activeAgent)
                                    ?.display_name
                            }
                        </CardTitle>
                        {currentOutput && (
                            <Badge
                                variant={
                                    currentOutput.status === "completed" ? "default" : "secondary"
                                }
                            >
                                {currentOutput.status === "completed" && "✅ 完成"}
                                {currentOutput.status === "running" && "⏳ 运行中"}
                                {currentOutput.status === "pending" && "⏸️ 等待"}
                            </Badge>
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="output">
                        <TabsList className="mb-4">
                            <TabsTrigger value="output">📝 输出内容</TabsTrigger>
                            <TabsTrigger value="prompt">💡 使用的提示词</TabsTrigger>
                        </TabsList>

                        <TabsContent value="output">
                            <div className="h-[400px] overflow-auto rounded-md border p-4">
                                {currentOutput ? (
                                    <pre className="whitespace-pre-wrap font-sans text-sm">
                                        {currentOutput.content}
                                    </pre>
                                ) : (
                                    <div className="flex h-full items-center justify-center text-muted-foreground">
                                        暂无输出 - 请先运行分析
                                    </div>
                                )}
                            </div>
                        </TabsContent>

                        <TabsContent value="prompt">
                            <div className="h-[400px] overflow-auto rounded-md border bg-muted/50 p-4">
                                {currentOutput?.prompt_used ? (
                                    <pre className="whitespace-pre-wrap text-sm">
                                        {currentOutput.prompt_used}
                                    </pre>
                                ) : (
                                    <div className="flex h-full items-center justify-center text-muted-foreground">
                                        暂无提示词信息
                                    </div>
                                )}
                            </div>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>
        </div>
    );
}
