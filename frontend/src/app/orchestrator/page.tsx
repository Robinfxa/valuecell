import { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnalysisPanel } from "./components/analysis-panel";
import { AgentOutputTabs } from "./components/agent-output-tabs";
import { PromptTemplates } from "./components/prompt-templates";

export default function OrchestratorPage() {
    const [activeTab, setActiveTab] = useState("analysis");

    return (
        <div className="flex size-full flex-col items-center justify-start gap-6 p-6">
            {/* Page Header */}
            <div className="w-full max-w-6xl">
                <h1 className="text-3xl font-bold">🎯 智能分析引擎</h1>
                <p className="mt-2 text-muted-foreground">
                    多Agent协作分析 · 实时显示每个Agent输出 · 自定义提示词模板
                </p>
            </div>

            {/* Main Content */}
            <div className="w-full max-w-6xl">
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="analysis">📊 分析面板</TabsTrigger>
                        <TabsTrigger value="outputs">📝 Agent输出</TabsTrigger>
                        <TabsTrigger value="templates">⚙️ 提示词模板</TabsTrigger>
                    </TabsList>

                    <TabsContent value="analysis" className="mt-4">
                        <AnalysisPanel />
                    </TabsContent>

                    <TabsContent value="outputs" className="mt-4">
                        <AgentOutputTabs />
                    </TabsContent>

                    <TabsContent value="templates" className="mt-4">
                        <PromptTemplates />
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
