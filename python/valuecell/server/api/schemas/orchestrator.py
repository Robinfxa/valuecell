"""Orchestrator API Schemas.

Pydantic models for orchestrator template and analysis endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .base import SuccessResponse


class PromptTemplateItem(BaseModel):
    """Prompt template item."""
    id: str
    name: str
    agent_type: str
    content: str
    variables: List[str] = Field(default_factory=list)
    description: str = ""
    is_default: bool = False
    created_at: str
    updated_at: str


class TemplateCreateRequest(BaseModel):
    """Request to create a template."""
    name: str
    agent_type: str
    content: str
    variables: List[str] = Field(default_factory=list)
    description: str = ""


class TemplateUpdateRequest(BaseModel):
    """Request to update a template."""
    name: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    description: Optional[str] = None


class TemplateSetItem(BaseModel):
    """Template set item."""
    id: str
    name: str
    description: str = ""
    template_ids: Dict[str, str] = Field(default_factory=dict)
    is_default: bool = False
    created_at: str


class TemplateSetCreateRequest(BaseModel):
    """Request to create a template set."""
    name: str
    description: str = ""
    template_ids: Dict[str, str] = Field(default_factory=dict)


class AnalysisRequest(BaseModel):
    """Request to start analysis."""
    query: str
    ticker: Optional[str] = None
    market_type: Optional[str] = "china"
    trade_date: Optional[str] = None
    selected_analysts: Optional[List[str]] = None
    template_set_id: Optional[str] = None


class AnalysisStartResponse(BaseModel):
    """Response after starting analysis."""
    task_id: str
    message: str


# Response type aliases using SuccessResponse
TemplateListResponse = SuccessResponse[List[PromptTemplateItem]]
TemplateItemResponse = SuccessResponse[PromptTemplateItem]
TemplateSetListResponse = SuccessResponse[List[TemplateSetItem]]
TemplateSetItemResponse = SuccessResponse[TemplateSetItem]
AnalysisStartSuccessResponse = SuccessResponse[AnalysisStartResponse]
