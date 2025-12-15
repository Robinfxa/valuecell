"""Orchestrator API Router.

Provides endpoints for prompt templates, template sets, and analysis.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from valuecell.server.api.schemas.base import SuccessResponse
from valuecell.server.api.schemas.orchestrator import (
    AnalysisRequest,
    AnalysisStartResponse,
    PromptTemplateItem,
    TemplateCreateRequest,
    TemplateSetCreateRequest,
    TemplateSetItem,
    TemplateUpdateRequest,
)

# Import the prompt template system
from valuecell.agents.market_analysis_orchestrator.prompts import (
    TemplateManager,
    AgentType,
)


def create_orchestrator_router() -> APIRouter:
    """Create orchestrator router with template and analysis endpoints."""
    
    router = APIRouter(
        prefix="/orchestrator",
        tags=["orchestrator"],
        responses={404: {"description": "Not found"}},
    )
    
    # Initialize template manager (in-memory for now)
    template_manager = TemplateManager()

    # ===== Template Endpoints =====

    @router.get(
        "/templates",
        response_model=SuccessResponse[list[PromptTemplateItem]],
        summary="List all prompt templates",
    )
    async def list_templates(agent_type: str = None):
        """Get all prompt templates, optionally filtered by agent type."""
        try:
            if agent_type and agent_type in AgentType.ALL:
                templates = template_manager.get_templates_by_agent(agent_type)
            else:
                templates = template_manager.list_templates()
            
            items = [PromptTemplateItem(**t.to_dict()) for t in templates]
            return SuccessResponse.create(
                data=items,
                msg=f"Found {len(items)} templates"
            )
        except Exception as e:
            logger.exception(f"Failed to list templates: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/templates/{template_id}",
        response_model=SuccessResponse[PromptTemplateItem],
        summary="Get a template by ID",
    )
    async def get_template(template_id: str):
        """Get a specific template by ID."""
        template = template_manager.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return SuccessResponse.create(
            data=PromptTemplateItem(**template.to_dict()),
            msg="Template found"
        )

    @router.post(
        "/templates",
        response_model=SuccessResponse[PromptTemplateItem],
        summary="Create a new template",
    )
    async def create_template(request: TemplateCreateRequest):
        """Create a new prompt template."""
        try:
            template = template_manager.create_template(
                name=request.name,
                agent_type=request.agent_type,
                content=request.content,
                variables=request.variables,
                description=request.description,
            )
            return SuccessResponse.create(
                data=PromptTemplateItem(**template.to_dict()),
                msg="Template created"
            )
        except Exception as e:
            logger.exception(f"Failed to create template: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.put(
        "/templates/{template_id}",
        response_model=SuccessResponse[PromptTemplateItem],
        summary="Update a template",
    )
    async def update_template(template_id: str, request: TemplateUpdateRequest):
        """Update an existing template."""
        kwargs = {k: v for k, v in request.model_dump().items() if v is not None}
        template = template_manager.update_template(template_id, **kwargs)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return SuccessResponse.create(
            data=PromptTemplateItem(**template.to_dict()),
            msg="Template updated"
        )

    @router.delete(
        "/templates/{template_id}",
        response_model=SuccessResponse[dict],
        summary="Delete a template",
    )
    async def delete_template(template_id: str):
        """Delete a template."""
        success = template_manager.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return SuccessResponse.create(
            data={"deleted": True, "template_id": template_id},
            msg="Template deleted"
        )

    # ===== Template Set Endpoints =====

    @router.get(
        "/template-sets",
        response_model=SuccessResponse[list[TemplateSetItem]],
        summary="List all template sets",
    )
    async def list_template_sets():
        """Get all template sets."""
        sets = template_manager.list_template_sets()
        items = [TemplateSetItem(**s.to_dict()) for s in sets]
        return SuccessResponse.create(
            data=items,
            msg=f"Found {len(items)} template sets"
        )

    @router.post(
        "/template-sets",
        response_model=SuccessResponse[TemplateSetItem],
        summary="Create a template set",
    )
    async def create_template_set(request: TemplateSetCreateRequest):
        """Create a new template set."""
        try:
            template_set = template_manager.create_template_set(
                name=request.name,
                description=request.description,
                template_ids=request.template_ids,
            )
            return SuccessResponse.create(
                data=TemplateSetItem(**template_set.to_dict()),
                msg="Template set created"
            )
        except Exception as e:
            logger.exception(f"Failed to create template set: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post(
        "/template-sets/{set_id}/apply",
        response_model=SuccessResponse[dict],
        summary="Apply a template set",
    )
    async def apply_template_set(set_id: str):
        """Apply a template set and return the templates."""
        templates = template_manager.apply_template_set(set_id)
        if not templates:
            raise HTTPException(status_code=404, detail="Template set not found")
        
        result = {
            agent_type: PromptTemplateItem(**t.to_dict()).model_dump()
            for agent_type, t in templates.items()
        }
        return SuccessResponse.create(
            data=result,
            msg=f"Applied template set with {len(result)} templates"
        )

    # ===== Analysis Endpoints =====

    @router.post(
        "/analyze",
        response_model=SuccessResponse[AnalysisStartResponse],
        summary="Start a multi-agent analysis",
    )
    async def start_analysis(request: AnalysisRequest):
        """Start a multi-agent analysis task."""
        import uuid
        
        # For now, return a mock task ID
        # TODO: Integrate with actual MarketAnalysisOrchestrator
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            f"Starting analysis: ticker={request.ticker}, "
            f"market={request.market_type}, analysts={request.selected_analysts}"
        )
        
        return SuccessResponse.create(
            data=AnalysisStartResponse(
                task_id=task_id,
                message=f"Analysis started for {request.ticker or request.query}"
            ),
            msg="Analysis task created"
        )

    return router
