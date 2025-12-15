import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useGetTemplates, useCreateTemplate, useUpdateTemplate } from "@/api/orchestrator";
import {
    ORCHESTRATOR_AGENTS,
    type OrchestratorAgentType,
    type PromptTemplate,
} from "@/types/orchestrator";
import { toast } from "sonner";

export function PromptTemplates() {
    const { data: templates = [], isLoading } = useGetTemplates();
    const createTemplate = useCreateTemplate();
    const updateTemplate = useUpdateTemplate();

    const [selectedAgent, setSelectedAgent] = useState<OrchestratorAgentType | "all">("all");
    const [editingTemplate, setEditingTemplate] = useState<PromptTemplate | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // New/Edit template form state
    const [formName, setFormName] = useState("");
    const [formAgentType, setFormAgentType] = useState<OrchestratorAgentType>("market_analyst");
    const [formContent, setFormContent] = useState("");
    const [formVariables, setFormVariables] = useState("");

    const filteredTemplates =
        selectedAgent === "all"
            ? templates
            : templates.filter((t) => t.agent_type === selectedAgent);

    const openEditDialog = (template: PromptTemplate) => {
        setEditingTemplate(template);
        setFormName(template.name);
        setFormAgentType(template.agent_type);
        setFormContent(template.content);
        setFormVariables(template.variables.join(", "));
        setIsDialogOpen(true);
    };

    const openNewDialog = () => {
        setEditingTemplate(null);
        setFormName("");
        setFormAgentType("market_analyst");
        setFormContent("");
        setFormVariables("");
        setIsDialogOpen(true);
    };

    const handleSave = async () => {
        const variables = formVariables
            .split(",")
            .map((v) => v.trim())
            .filter(Boolean);

        try {
            if (editingTemplate) {
                await updateTemplate.mutateAsync({
                    id: editingTemplate.id,
                    name: formName,
                    content: formContent,
                    variables,
                });
                toast.success("模板已更新");
            } else {
                await createTemplate.mutateAsync({
                    name: formName,
                    agent_type: formAgentType,
                    content: formContent,
                    variables,
                });
                toast.success("模板已创建");
            }
            setIsDialogOpen(false);
        } catch (error) {
            toast.error("保存失败");
        }
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Label>筛选 Agent:</Label>
                    <Select
                        value={selectedAgent}
                        onValueChange={(v) => setSelectedAgent(v as typeof selectedAgent)}
                    >
                        <SelectTrigger className="w-48">
                            <SelectValue placeholder="全部 Agent" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">全部 Agent</SelectItem>
                            {ORCHESTRATOR_AGENTS.map((agent) => (
                                <SelectItem key={agent.type} value={agent.type}>
                                    {agent.icon} {agent.display_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <Button onClick={openNewDialog}>
                    ➕ 新建模板
                </Button>
            </div>

            {/* Templates Grid */}
            {isLoading ? (
                <div className="p-8 text-center text-muted-foreground">加载中...</div>
            ) : filteredTemplates.length === 0 ? (
                <Card>
                    <CardContent className="p-8 text-center text-muted-foreground">
                        暂无模板 - 点击"新建模板"创建
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-2 gap-4">
                    {filteredTemplates.map((template) => {
                        const agent = ORCHESTRATOR_AGENTS.find(
                            (a) => a.type === template.agent_type
                        );
                        return (
                            <Card
                                key={template.id}
                                className="cursor-pointer transition-shadow hover:shadow-md"
                                onClick={() => openEditDialog(template)}
                            >
                                <CardHeader className="pb-2">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="flex items-center gap-2 text-base">
                                            {agent?.icon} {template.name}
                                        </CardTitle>
                                        {template.is_default && (
                                            <Badge variant="secondary">默认</Badge>
                                        )}
                                    </div>
                                    <p className="text-sm text-muted-foreground">
                                        {agent?.display_name}
                                    </p>
                                </CardHeader>
                                <CardContent>
                                    <div className="mb-2 flex flex-wrap gap-1">
                                        {template.variables.slice(0, 4).map((v) => (
                                            <Badge key={v} variant="outline" className="text-xs">
                                                {`{${v}}`}
                                            </Badge>
                                        ))}
                                        {template.variables.length > 4 && (
                                            <Badge variant="outline" className="text-xs">
                                                +{template.variables.length - 4}
                                            </Badge>
                                        )}
                                    </div>
                                    <p className="line-clamp-2 text-sm text-muted-foreground">
                                        {template.content.slice(0, 100)}...
                                    </p>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            {/* Edit/Create Dialog */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent className="max-w-3xl">
                    <DialogHeader>
                        <DialogTitle>
                            {editingTemplate ? "编辑模板" : "新建模板"}
                        </DialogTitle>
                    </DialogHeader>

                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">模板名称</Label>
                                <Input
                                    id="name"
                                    value={formName}
                                    onChange={(e) => setFormName(e.target.value)}
                                    placeholder="如: 激进技术分析"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="agent_type">Agent 类型</Label>
                                <Select
                                    value={formAgentType}
                                    onValueChange={(v) => setFormAgentType(v as OrchestratorAgentType)}
                                    disabled={!!editingTemplate}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {ORCHESTRATOR_AGENTS.map((agent) => (
                                            <SelectItem key={agent.type} value={agent.type}>
                                                {agent.icon} {agent.display_name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="variables">变量 (逗号分隔)</Label>
                            <Input
                                id="variables"
                                value={formVariables}
                                onChange={(e) => setFormVariables(e.target.value)}
                                placeholder="如: ticker, company_name, trade_date"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="content">提示词内容</Label>
                            <Textarea
                                id="content"
                                value={formContent}
                                onChange={(e) => setFormContent(e.target.value)}
                                placeholder="输入提示词内容，使用 {变量名} 作为占位符..."
                                className="min-h-[300px] font-mono text-sm"
                            />
                        </div>
                    </div>

                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                            取消
                        </Button>
                        <Button onClick={handleSave} disabled={!formName || !formContent}>
                            保存
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
