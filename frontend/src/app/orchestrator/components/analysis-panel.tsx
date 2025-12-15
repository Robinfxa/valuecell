import { useState } from "react";
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
import { useStartAnalysis, useGetTemplateSets } from "@/api/orchestrator";
import {
    ORCHESTRATOR_AGENTS,
    type OrchestratorAgentType,
} from "@/types/orchestrator";

export function AnalysisPanel() {
    const [ticker, setTicker] = useState("");
    const [marketType, setMarketType] = useState<"china" | "hk" | "us">("china");
    const [selectedAgents, setSelectedAgents] = useState<OrchestratorAgentType[]>([
        "market_analyst",
        "fundamentals_analyst",
    ]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [progress, setProgress] = useState(0);

    const { data: templateSets = [] } = useGetTemplateSets();
    const startAnalysis = useStartAnalysis();

    const toggleAgent = (agentType: OrchestratorAgentType) => {
        setSelectedAgents((prev) =>
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

    const analysts = ORCHESTRATOR_AGENTS.filter((a) => a.category === "analyst");
    const researchers = ORCHESTRATOR_AGENTS.filter(
        (a) => a.category === "researcher"
    );
    const riskAgents = ORCHESTRATOR_AGENTS.filter((a) => a.category === "risk");

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
                <CardContent className="space-y-4">
                    {/* Analysts */}
                    <div>
                        <Label className="mb-2 block text-sm text-muted-foreground">
                            分析师
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {analysts.map((agent) => (
                                <Badge
                                    key={agent.type}
                                    variant={
                                        selectedAgents.includes(agent.type) ? "default" : "outline"
                                    }
                                    className="cursor-pointer px-3 py-1.5 text-sm"
                                    onClick={() =>
                                        !isAnalyzing && toggleAgent(agent.type)
                                    }
                                >
                                    {agent.icon} {agent.display_name}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    {/* Researchers */}
                    <div>
                        <Label className="mb-2 block text-sm text-muted-foreground">
                            研究员
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {researchers.map((agent) => (
                                <Badge
                                    key={agent.type}
                                    variant={
                                        selectedAgents.includes(agent.type) ? "default" : "outline"
                                    }
                                    className="cursor-pointer px-3 py-1.5 text-sm"
                                    onClick={() =>
                                        !isAnalyzing && toggleAgent(agent.type)
                                    }
                                >
                                    {agent.icon} {agent.display_name}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    {/* Risk Management */}
                    <div>
                        <Label className="mb-2 block text-sm text-muted-foreground">
                            风险管理
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {riskAgents.map((agent) => (
                                <Badge
                                    key={agent.type}
                                    variant={
                                        selectedAgents.includes(agent.type) ? "default" : "outline"
                                    }
                                    className="cursor-pointer px-3 py-1.5 text-sm"
                                    onClick={() =>
                                        !isAnalyzing && toggleAgent(agent.type)
                                    }
                                >
                                    {agent.icon} {agent.display_name}
                                </Badge>
                            ))}
                        </div>
                    </div>
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
                            disabled={!ticker.trim() || selectedAgents.length === 0}
                        >
                            🚀 开始智能分析
                        </Button>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
