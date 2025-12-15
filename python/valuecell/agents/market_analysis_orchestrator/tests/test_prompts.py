"""Tests for prompt template management."""

import pytest

from valuecell.agents.market_analysis_orchestrator.prompts import (
    AgentType,
    DEFAULT_TEMPLATES,
    PromptTemplate,
    TemplateManager,
    TemplateSet,
)


class TestPromptTemplate:
    """Tests for PromptTemplate class."""

    def test_create_template(self):
        """Test creating a template."""
        template = PromptTemplate(
            id="test_id",
            name="Test Template",
            agent_type="market_analyst",
            content="Hello {name}!",
            variables=["name"],
        )
        assert template.id == "test_id"
        assert template.name == "Test Template"

    def test_render_template(self):
        """Test rendering a template with variables."""
        template = PromptTemplate(
            id="test",
            name="Test",
            agent_type="test",
            content="Stock: {ticker}, Date: {date}",
            variables=["ticker", "date"],
        )
        result = template.render(ticker="AAPL", date="2025-12-15")
        assert "AAPL" in result
        assert "2025-12-15" in result

    def test_render_missing_variable(self):
        """Test rendering with missing variable uses placeholder."""
        template = PromptTemplate(
            id="test",
            name="Test",
            agent_type="test",
            content="Hello {name}!",
            variables=["name"],
        )
        result = template.render()  # Missing name
        assert "[name]" in result

    def test_to_dict(self):
        """Test serialization to dict."""
        template = PromptTemplate(
            id="test",
            name="Test",
            agent_type="test",
            content="Content",
        )
        data = template.to_dict()
        assert data["id"] == "test"
        assert data["name"] == "Test"
        assert "created_at" in data

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "id": "test",
            "name": "Test",
            "agent_type": "test",
            "content": "Content",
        }
        template = PromptTemplate.from_dict(data)
        assert template.id == "test"


class TestTemplateManager:
    """Tests for TemplateManager class."""

    @pytest.fixture
    def manager(self):
        return TemplateManager()

    def test_list_templates(self, manager):
        """Test listing templates."""
        templates = manager.list_templates()
        assert len(templates) >= 11  # Default templates

    def test_get_template(self, manager):
        """Test getting template by ID."""
        template = manager.get_template("default_market")
        assert template is not None
        assert template.agent_type == AgentType.MARKET_ANALYST

    def test_get_templates_by_agent(self, manager):
        """Test getting templates by agent type."""
        templates = manager.get_templates_by_agent(AgentType.MARKET_ANALYST)
        assert len(templates) >= 1
        assert all(t.agent_type == AgentType.MARKET_ANALYST for t in templates)

    def test_get_default_template(self, manager):
        """Test getting default template."""
        template = manager.get_default_template(AgentType.MARKET_ANALYST)
        assert template is not None
        assert template.is_default

    def test_create_template(self, manager):
        """Test creating a new template."""
        template = manager.create_template(
            name="Custom Template",
            agent_type="test_agent",
            content="Custom content {var1}",
            variables=["var1"],
        )
        assert template.id is not None
        assert template.name == "Custom Template"

        # Verify retrieval
        retrieved = manager.get_template(template.id)
        assert retrieved is not None

    def test_update_template(self, manager):
        """Test updating a template."""
        template = manager.create_template(
            name="Original",
            agent_type="test",
            content="Original content",
        )
        updated = manager.update_template(template.id, name="Updated")
        assert updated.name == "Updated"

    def test_delete_template(self, manager):
        """Test deleting a template."""
        template = manager.create_template(
            name="ToDelete",
            agent_type="test",
            content="Content",
        )
        assert manager.delete_template(template.id)
        assert manager.get_template(template.id) is None


class TestTemplateSet:
    """Tests for TemplateSet class."""

    def test_create_template_set(self):
        """Test creating a template set."""
        template_set = TemplateSet(
            id="test_set",
            name="Test Set",
            template_ids={
                AgentType.MARKET_ANALYST: "default_market",
                AgentType.BULL_RESEARCHER: "default_bull",
            },
        )
        assert template_set.id == "test_set"
        assert len(template_set.template_ids) == 2

    def test_template_manager_apply_set(self):
        """Test applying a template set."""
        manager = TemplateManager()
        template_set = manager.create_template_set(
            name="Aggressive Strategy",
            template_ids={
                AgentType.MARKET_ANALYST: "default_market",
            },
            description="Aggressive trading templates",
        )

        applied = manager.apply_template_set(template_set.id)
        assert AgentType.MARKET_ANALYST in applied


class TestAgentType:
    """Tests for AgentType constants."""

    def test_all_types(self):
        """Test that all agent types are defined."""
        assert len(AgentType.ALL) == 12
        assert AgentType.MARKET_ANALYST in AgentType.ALL
        assert AgentType.TRADER_AI in AgentType.ALL


class TestDefaultTemplates:
    """Tests for default templates."""

    def test_default_templates_count(self):
        """Test default templates are loaded."""
        assert len(DEFAULT_TEMPLATES) == 11

    def test_default_templates_have_content(self):
        """Test all default templates have content."""
        for template in DEFAULT_TEMPLATES:
            assert template.content
            assert len(template.content) > 50

    def test_default_templates_have_variables(self):
        """Test all default templates have variables defined."""
        for template in DEFAULT_TEMPLATES:
            assert len(template.variables) >= 1
