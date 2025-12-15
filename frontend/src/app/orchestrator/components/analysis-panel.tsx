import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useStartAnalysis, useGetTemplateSets } from "@/api/orchestrator";
import {
    ORCHESTRATOR_AGENTS,
    type OrchestratorAgentType,
} from "@/types/orchestrator";

// 必选分析师 - 不可取消
const CORE_AGENTS: OrchestratorAgentType[] = [
    "market_analyst",
    "fundamentals_analyst",
    "research_manager",
];

// 可选分析师
const OPTIONAL_ANALYSTS: OrchestratorAgentType[] = [
    "news_analyst",
    "social_analyst",
];

// 辩论组 - 成对开启
const DEBATE_PAIRS = {
    research: ["bull_researcher", "bear_researcher"] as OrchestratorAgentType[],
    risk: [
        "risky_debater",
        "safe_debater",
        "neutral_debater",
        "risk_manager",
    ] as OrchestratorAgentType[],
};

export function AnalysisPanel() {
    const [ticker, setTicker] = useState("");
    const [marketType, setMarketType] = useState<"china" | "hk" | "us">("china");
    // 核心分析师默认选中且不可取消
    const [optionalAgents, setOptionalAgents] = useState<OrchestratorAgentType[]>(
        []
    );
    const [enableResearchDebate, setEnableResearchDebate] = useState(false);
    const [enableRiskDebate, setEnableRiskDebate] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [progress, setProgress] = useState(0);

    const { data: templateSets = [] } = useGetTemplateSets();
    const startAnalysis = useStartAnalysis();

    // 计算最终选中的分析师
    const selectedAgents: OrchestratorAgentType[] = [
        ...CORE_AGENTS,
        ...optionalAgents,
        ...(enableResearchDebate ? DEBATE_PAIRS.research : []),
        ...(enableRiskDebate ? DEBATE_PAIRS.risk : []),
    ];

    const toggleOptionalAgent = (agentType: OrchestratorAgentType) => {
        setOptionalAgents((prev) =>
            prev.includes(agentType)
                ? prev.filter((a) => a !== agentType)
                : [...prev, agentType]
        );
    };

    const handleStartAnalysis = async () => {
        if (!ticker.trim()) return;

        setIsAnalyzing(true);
        setProgress(0);

        try {
            await startAnalysis.mutateAsync({
                query: `分析 ${ticker}`,
                ticker,
                market_type: marketType,
                selected_analysts: selectedAgents,
            });

            // Simulate progress (actual progress would come from SSE)
            const interval = setInterval(() => {
                setProgress((p) => {
                    if (p >= 100) {
                        clearInterval(interval);
                        setIsAnalyzing(false);
                        return 100;
                    }
                    return p + 10;
                });
            }, 1000);
        } catch (error) {
            console.error("Analysis failed:", error);
            setIsAnalyzing(false);
        }
    };

    // 获取分析师信息
    const getAgentInfo = (type: OrchestratorAgentType) =>
        ORCHESTRATOR_AGENTS.find((a) => a.type === type);

    return (
        <div className="space-y-6">
            {/* Input Section */}
            <Card>
                <CardHeader>
                    <CardTitle>📋 分析配置</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="ticker">股票代码</Label>
                            <Input
                                id="ticker"
                                placeholder="如: 000001.SZ, AAPL, 0700.HK"
                                value={ticker}
                                onChange={(e) => setTicker(e.target.value)}
                                disabled={isAnalyzing}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="market">市场类型</Label>
                            <Select
                                value={marketType}
                                onValueChange={(v) => setMarketType(v as typeof marketType)}
                                disabled={isAnalyzing}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="选择市场" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="china">🇨🇳 A股市场</SelectItem>
                                    <SelectItem value="hk">🇭🇰 港股市场</SelectItem>
                                    <SelectItem value="us">🇺🇸 美股市场</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Template Set Selection */}
                    {templateSets.length > 0 && (
                        <div className="space-y-2">
                            <Label>模板集</Label>
                            <Select>
                                <SelectTrigger>
                                    <SelectValue placeholder="使用默认模板" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="default">默认模板</SelectItem>
                                    {templateSets.map((set) => (
                                        <SelectItem key={set.id} value={set.id}>
                                            {set.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Agent Selection */}
            <Card>
                <CardHeader>
                    <CardTitle>👥 分析师团队</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Core Agents - 必选 */}
                    <div>
                        <Label className="mb-2 flex items-center gap-2 text-sm">
                            <span className="text-green-600">●</span> 核心分析师 (必选)
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {CORE_AGENTS.map((type) => {
                                const agent = getAgentInfo(type);
                                return (
                                    <Badge
                                        key={type}
                                        variant="default"
                                        className="cursor-not-allowed px-3 py-1.5 text-sm opacity-90"
                                    >
                                        {agent?.icon} {agent?.display_name} ✓
                                    </Badge>
                                );
                            })}
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">
                            技术面 + 基本面 + 研究经理 构成核心分析流程
                        </p>
                    </div>

                    {/* Optional Analysts */}
                    <div>
                        <Label className="mb-2 flex items-center gap-2 text-sm">
                            <span className="text-blue-600">○</span> 可选分析师
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {OPTIONAL_ANALYSTS.map((type) => {
                                const agent = getAgentInfo(type);
                                return (
                                    <Badge
                                        key={type}
                                        variant={optionalAgents.includes(type) ? "default" : "outline"}
                                        className="cursor-pointer px-3 py-1.5 text-sm"
                                        onClick={() => !isAnalyzing && toggleOptionalAgent(type)}
                                    >
                                        {agent?.icon} {agent?.display_name}
                                    </Badge>
                                );
                            })}
                        </div>
                    </div>

                    {/* Debate Groups */}
                    <div>
                        <Label className="mb-2 flex items-center gap-2 text-sm">
                            <span className="text-purple-600">◐</span> 辩论组 (整组开启)
                        </Label>
                        <div className="space-y-3">
                            {/* Research Debate */}
                            <div className="flex items-center gap-3">
                                <Button
                                    variant={enableResearchDebate ? "default" : "outline"}
                                    size="sm"
                                    onClick={() =>
                                        !isAnalyzing && setEnableResearchDebate(!enableResearchDebate)
                                    }
                                    disabled={isAnalyzing}
                                >
                                    {enableResearchDebate ? "✓ " : ""}🐂🐻 多空辩论
                                </Button>
                                <span className="text-xs text-muted-foreground">
                                    看涨研究员 vs 看跌研究员
                                </span>
                            </div>

                            {/* Risk Debate */}
                            <div className="flex items-center gap-3">
                                <Button
                                    variant={enableRiskDebate ? "default" : "outline"}
                                    size="sm"
                                    onClick={() =>
                                        !isAnalyzing && setEnableRiskDebate(!enableRiskDebate)
                                    }
                                    disabled={isAnalyzing}
                                >
                                    {enableRiskDebate ? "✓ " : ""}⚖️ 风险辩论
                                </Button>
                                <span className="text-xs text-muted-foreground">
                                    激进 vs 保守 vs 中性 + 风险经理
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Summary */}
                    <Alert>
                        <AlertDescription>
                            已选择 <strong>{selectedAgents.length}</strong> 个分析师:{" "}
                            {selectedAgents
                                .map((type) => getAgentInfo(type)?.display_name)
                                .join(" → ")}
                        </AlertDescription>
                    </Alert>
                </CardContent>
            </Card>

            {/* Start Button & Progress */}
            <Card>
                <CardContent className="pt-6">
                    {isAnalyzing ? (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">分析进行中...</span>
                                <span className="text-sm text-muted-foreground">{progress}%</span>
                            </div>
                            <Progress value={progress} className="w-full" />
                            <p className="text-center text-sm text-muted-foreground">
                                🔄 正在运行 {selectedAgents.length} 个分析Agent...
                            </p>
                        </div>
                    ) : (
                        <Button
                            className="w-full"
                            size="lg"
                            onClick={handleStartAnalysis}
                            disabled={!ticker.trim()}
                        >
                            🚀 开始智能分析 ({selectedAgents.length} 个Agent)
                        </Button>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
