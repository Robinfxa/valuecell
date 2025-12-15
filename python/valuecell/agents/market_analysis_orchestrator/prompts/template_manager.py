"""Template manager for prompt CRUD operations.

Provides in-memory and file-based storage for prompt templates.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from loguru import logger

from .base import AgentType, PromptTemplate, TemplateSet


class TemplateManager:
    """Manages prompt templates with CRUD operations.

    Supports both in-memory storage and JSON file persistence.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize template manager.

        Args:
            storage_path: Optional path for JSON file storage
        """
        self.storage_path = storage_path
        self._templates: Dict[str, PromptTemplate] = {}
        self._template_sets: Dict[str, TemplateSet] = {}

        # Load from file if exists
        if storage_path and os.path.exists(storage_path):
            self._load_from_file()

        # Load defaults if empty
        if not self._templates:
            self._load_default_templates()

    def _load_from_file(self) -> None:
        """Load templates from JSON file."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for t_data in data.get("templates", []):
                template = PromptTemplate.from_dict(t_data)
                self._templates[template.id] = template

            for s_data in data.get("template_sets", []):
                template_set = TemplateSet.from_dict(s_data)
                self._template_sets[template_set.id] = template_set

            logger.info(
                f"Loaded {len(self._templates)} templates and "
                f"{len(self._template_sets)} sets from {self.storage_path}"
            )
        except Exception as e:
            logger.exception(f"Failed to load templates: {e}")

    def _save_to_file(self) -> None:
        """Save templates to JSON file."""
        if not self.storage_path:
            return

        try:
            data = {
                "templates": [t.to_dict() for t in self._templates.values()],
                "template_sets": [s.to_dict() for s in self._template_sets.values()],
            }

            # Ensure directory exists
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved templates to {self.storage_path}")
        except Exception as e:
            logger.exception(f"Failed to save templates: {e}")

    def _load_default_templates(self) -> None:
        """Load default templates from agent modules."""
        from .defaults import DEFAULT_TEMPLATES

        for template in DEFAULT_TEMPLATES:
            self._templates[template.id] = template

        logger.info(f"Loaded {len(DEFAULT_TEMPLATES)} default templates")

    # ===== Template CRUD =====

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def get_templates_by_agent(self, agent_type: str) -> List[PromptTemplate]:
        """Get all templates for a specific agent type."""
        return [
            t for t in self._templates.values() if t.agent_type == agent_type
        ]

    def get_default_template(self, agent_type: str) -> Optional[PromptTemplate]:
        """Get the default template for an agent type."""
        for t in self._templates.values():
            if t.agent_type == agent_type and t.is_default:
                return t
        # Return first if no default
        templates = self.get_templates_by_agent(agent_type)
        return templates[0] if templates else None

    def list_templates(self) -> List[PromptTemplate]:
        """List all templates."""
        return list(self._templates.values())

    def create_template(
        self,
        name: str,
        agent_type: str,
        content: str,
        variables: Optional[List[str]] = None,
        description: str = "",
        is_default: bool = False,
    ) -> PromptTemplate:
        """Create a new template."""
        template_id = str(uuid.uuid4())[:8]

        template = PromptTemplate(
            id=template_id,
            name=name,
            agent_type=agent_type,
            content=content,
            variables=variables or [],
            description=description,
            is_default=is_default,
        )

        self._templates[template_id] = template
        self._save_to_file()

        logger.info(f"Created template: {name} ({template_id})")
        return template

    def update_template(
        self,
        template_id: str,
        **kwargs: Any,
    ) -> Optional[PromptTemplate]:
        """Update an existing template."""
        template = self._templates.get(template_id)
        if not template:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now()
        self._save_to_file()

        logger.info(f"Updated template: {template_id}")
        return template

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            self._save_to_file()
            logger.info(f"Deleted template: {template_id}")
            return True
        return False

    # ===== Template Set CRUD =====

    def get_template_set(self, set_id: str) -> Optional[TemplateSet]:
        """Get a template set by ID."""
        return self._template_sets.get(set_id)

    def list_template_sets(self) -> List[TemplateSet]:
        """List all template sets."""
        return list(self._template_sets.values())

    def create_template_set(
        self,
        name: str,
        template_ids: Dict[str, str],
        description: str = "",
    ) -> TemplateSet:
        """Create a new template set."""
        set_id = str(uuid.uuid4())[:8]

        template_set = TemplateSet(
            id=set_id,
            name=name,
            description=description,
            template_ids=template_ids,
        )

        self._template_sets[set_id] = template_set
        self._save_to_file()

        logger.info(f"Created template set: {name} ({set_id})")
        return template_set

    def apply_template_set(self, set_id: str) -> Dict[str, PromptTemplate]:
        """Apply a template set and return the templates.

        Returns:
            Dict mapping agent_type to PromptTemplate
        """
        template_set = self._template_sets.get(set_id)
        if not template_set:
            return {}

        result = {}
        for agent_type, template_id in template_set.template_ids.items():
            template = self._templates.get(template_id)
            if template:
                result[agent_type] = template

        return result

    def get_all_prompts_with_details(self) -> List[Dict[str, Any]]:
        """Get all templates with full details for frontend display.

        Returns:
            List of template details including content, variables, etc.
        """
        return [t.to_dict() for t in self._templates.values()]
