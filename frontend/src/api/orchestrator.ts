import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { API_QUERY_KEYS } from "@/constants/api";
import { type ApiResponse, apiClient } from "@/lib/api-client";
import type {
    AnalysisRequest,
    AnalysisResult,
    PromptTemplate,
    TemplateSet,
} from "@/types/orchestrator";

// ===== Templates =====

export const useGetTemplates = () => {
    return useQuery({
        queryKey: ["orchestrator", "templates"],
        queryFn: () =>
            apiClient.get<ApiResponse<PromptTemplate[]>>("/orchestrator/templates"),
        select: (data) => data.data,
    });
};

export const useGetTemplatesByAgent = (agentType: string) => {
    return useQuery({
        queryKey: ["orchestrator", "templates", agentType],
        queryFn: () =>
            apiClient.get<ApiResponse<PromptTemplate[]>>(
                `/orchestrator/templates?agent_type=${agentType}`
            ),
        select: (data) => data.data,
        enabled: !!agentType,
    });
};

export const useCreateTemplate = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (
            data: Pick<PromptTemplate, "name" | "agent_type" | "content" | "variables">
        ) =>
            apiClient.post<ApiResponse<PromptTemplate>>(
                "/orchestrator/templates",
                data
            ),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["orchestrator", "templates"],
            });
        },
    });
};

export const useUpdateTemplate = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            id,
            ...data
        }: Partial<PromptTemplate> & { id: string }) =>
            apiClient.put<ApiResponse<PromptTemplate>>(
                `/orchestrator/templates/${id}`,
                data
            ),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["orchestrator", "templates"],
            });
        },
    });
};

export const useDeleteTemplate = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (templateId: string) =>
            apiClient.delete<ApiResponse<null>>(`/orchestrator/templates/${templateId}`),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["orchestrator", "templates"],
            });
        },
    });
};

// ===== Template Sets =====

export const useGetTemplateSets = () => {
    return useQuery({
        queryKey: ["orchestrator", "template-sets"],
        queryFn: () =>
            apiClient.get<ApiResponse<TemplateSet[]>>("/orchestrator/template-sets"),
        select: (data) => data.data,
    });
};

export const useCreateTemplateSet = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: Pick<TemplateSet, "name" | "description" | "template_ids">) =>
            apiClient.post<ApiResponse<TemplateSet>>(
                "/orchestrator/template-sets",
                data
            ),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["orchestrator", "template-sets"],
            });
        },
    });
};

export const useApplyTemplateSet = () => {
    return useMutation({
        mutationFn: (setId: string) =>
            apiClient.post<ApiResponse<Record<string, PromptTemplate>>>(
                `/orchestrator/template-sets/${setId}/apply`
            ),
    });
};

// ===== Analysis =====

export const useStartAnalysis = () => {
    return useMutation({
        mutationFn: (data: AnalysisRequest) =>
            apiClient.post<ApiResponse<{ task_id: string; message: string }>>(
                "/orchestrator/analyze",
                data
            ),
    });
};

export const useGetAnalysisHistory = () => {
    return useQuery({
        queryKey: ["orchestrator", "history"],
        queryFn: () =>
            apiClient.get<ApiResponse<AnalysisResult[]>>("/orchestrator/history"),
        select: (data) => data.data,
    });
};

export const useGetAnalysisResult = (taskId?: string) => {
    return useQuery({
        queryKey: ["orchestrator", "result", taskId],
        queryFn: () =>
            apiClient.get<ApiResponse<AnalysisResult>>(
                `/orchestrator/result/${taskId}`
            ),
        select: (data) => data.data,
        enabled: !!taskId,
        refetchInterval: 3000, // Poll for updates
    });
};
