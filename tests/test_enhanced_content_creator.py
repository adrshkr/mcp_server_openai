"""
Tests for enhanced content creation tool with MCP server integration.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from mcp_server_openai.tools.enhanced_content_creator import (
    ContentPlan,
    ContentRequest,
    MCPClient,
    SlideContent,
    _convert_to_outline,
    _save_enhanced_ppt,
    create_enhanced_presentation,
)


class TestContentRequest:
    """Test ContentRequest dataclass."""

    def test_content_request_creation(self):
        """Test creating a ContentRequest instance."""
        request = ContentRequest(
            number_of_slides=5,
            brief="Test presentation",
            notes="Test notes",
            style="professional",
            tone="concise",
            audience="stakeholders",
            client_id="test_client",
        )

        assert request.number_of_slides == 5
        assert request.brief == "Test presentation"
        assert request.notes == "Test notes"
        assert request.style == "professional"
        assert request.tone == "concise"
        assert request.audience == "stakeholders"
        assert request.client_id == "test_client"

    def test_content_request_defaults(self):
        """Test ContentRequest with default values."""
        request = ContentRequest(number_of_slides=3, brief="Simple presentation", notes="Simple notes")

        assert request.style == "professional"
        assert request.tone == "concise"
        assert request.audience == "stakeholders"
        assert request.client_id is None


class TestSlideContent:
    """Test SlideContent dataclass."""

    def test_slide_content_creation(self):
        """Test creating a SlideContent instance."""
        slide = SlideContent(title="Test Slide", content=["Point 1", "Point 2"], slide_type="content")

        assert slide.title == "Test Slide"
        assert slide.content == ["Point 1", "Point 2"]
        assert slide.slide_type == "content"

    def test_slide_content_defaults(self):
        """Test SlideContent with default values."""
        slide = SlideContent(title="Default Slide", content=["Default content"])

        assert slide.slide_type == "content"


class TestContentPlan:
    """Test ContentPlan dataclass."""

    def test_content_plan_creation(self):
        """Test creating a ContentPlan instance."""
        slides = [SlideContent("Slide 1", ["Content 1"])]
        plan = ContentPlan(
            title="Test Plan",
            overview="Test overview",
            slides=slides,
            key_messages=["Message 1"],
            call_to_action="Test action",
        )

        assert plan.title == "Test Plan"
        assert plan.overview == "Test overview"
        assert len(plan.slides) == 1
        assert plan.key_messages == ["Message 1"]
        assert plan.call_to_action == "Test action"


class TestMCPClient:
    """Test MCPClient class."""

    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self):
        """Test MCPClient initialization."""
        client = MCPClient()
        assert client.servers == {}

    @pytest.mark.asyncio
    async def test_call_sequential_thinking(self):
        """Test calling sequential thinking server."""
        client = MCPClient()
        result = await client.call_server(
            "sequential_thinking",
            "plan_presentation",
            {"brief": "Test brief", "notes": "Test notes", "number_of_slides": 3},
        )

        assert "title" in result
        assert "slides" in result
        assert "key_messages" in result

    @pytest.mark.asyncio
    async def test_call_brave_search(self):
        """Test calling brave search server."""
        client = MCPClient()
        result = await client.call_server("brave_search", "search_content", {"query": "test query"})

        assert "search_results" in result
        assert "additional_context" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_call_memory(self):
        """Test calling memory server."""
        client = MCPClient()
        result = await client.call_server("memory", "generate_content", {"slide_info": {"title": "Test Slide"}})

        assert "title" in result
        assert "bullet_points" in result
        assert "visual_suggestions" in result
        assert "speaker_notes" in result

    @pytest.mark.asyncio
    async def test_call_unknown_server(self):
        """Test calling unknown server."""
        client = MCPClient()
        result = await client.call_server("unknown_server", "test_method", {})

        assert "error" in result
        assert "Unknown server" in result["error"]

    @pytest.mark.asyncio
    async def test_call_unknown_method(self):
        """Test calling unknown method on known server."""
        client = MCPClient()
        result = await client.call_server("sequential_thinking", "unknown_method", {})

        assert "error" in result
        assert "Unknown method" in result["error"]


class TestConvertToOutline:
    """Test _convert_to_outline function."""

    def test_convert_to_outline(self):
        """Test converting content plan to outline format."""
        plan = {
            "slides": [
                {"title": "Slide 1", "bullet_points": ["Point 1", "Point 2"]},
                {"title": "Slide 2", "bullet_points": ["Point 3"]},
            ]
        }
        slides = [
            {"title": "Slide 1", "bullet_points": ["Point 1", "Point 2"]},
            {"title": "Slide 2", "bullet_points": ["Point 3"]},
        ]
        enhanced = {"search_results": ["Enhanced 1", "Enhanced 2"]}

        outline = _convert_to_outline(plan, slides, enhanced)

        assert len(outline) == 2
        assert outline[0][0] == "Slide 1"
        assert outline[0][1] == ["Point 1", "Point 2", "Enhanced 1", "Enhanced 2"]
        assert outline[1][0] == "Slide 2"
        assert outline[1][1] == ["Point 3", "Enhanced 1", "Enhanced 2"]

    def test_convert_to_outline_empty_content(self):
        """Test converting outline with empty content."""
        plan = {"slides": []}
        slides = []
        enhanced = {}

        outline = _convert_to_outline(plan, slides, enhanced)

        assert outline == []

    def test_convert_to_outline_missing_fields(self):
        """Test converting outline with missing fields."""
        plan = {"slides": [{"title": "Slide 1"}]}
        slides = [{"title": "Slide 1"}]
        enhanced = {}

        outline = _convert_to_outline(plan, slides, enhanced)

        assert len(outline) == 1
        assert outline[0][0] == "Slide 1"
        assert outline[0][1] == []


class TestSaveEnhancedPPT:
    """Test _save_enhanced_ppt function."""

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", create=True)
    def test_save_enhanced_ppt(self, mock_open, mock_mkdir):
        """Test saving enhanced presentation."""
        # Mock presentation object
        mock_presentation = type("MockPresentation", (), {"save": lambda self, path: None})()

        output_path = _save_enhanced_ppt(mock_presentation, "test_client", "test_project")

        assert "test_client" in str(output_path)
        assert "test_project" in str(output_path)
        assert "enhanced_presentation_" in str(output_path)
        assert output_path.suffix == ".pptx"


class TestCreateEnhancedPresentation:
    """Test create_enhanced_presentation function."""

    @pytest.mark.asyncio
    @patch("mcp_server_openai.tools.enhanced_content_creator.MCPClient")
    @patch("mcp_server_openai.tools.enhanced_content_creator._convert_to_outline")
    @patch("mcp_server_openai.tools.enhanced_content_creator._save_enhanced_ppt")
    async def test_create_enhanced_presentation_success(self, mock_save, mock_convert, mock_client_class):
        """Test successful presentation creation."""
        # Mock MCP client
        mock_client = AsyncMock()
        mock_client.call_server.side_effect = [
            {"slides": [{"title": "Slide 1", "bullet_points": ["Point 1"]}]},
            {"search_results": ["Enhanced 1"]},
            {"title": "Slide 1", "bullet_points": ["Point 1", "Enhanced 1"]},
        ]
        mock_client_class.return_value = mock_client

        # Mock outline conversion
        mock_convert.return_value = [("Slide 1", ["Point 1", "Enhanced 1"])]

        # Mock presentation creation and saving
        mock_presentation = type("MockPresentation", (), {})()
        mock_save.return_value = Path("output/test/enhanced_presentation.pptx")

        # Mock content creator imports
        with patch(
            "mcp_server_openai.tools.enhanced_content_creator._create_ppt_from_outline", create=True
        ) as mock_create:
            mock_create.return_value = mock_presentation

            result = await create_enhanced_presentation(
                number_of_slides=3,
                brief="Test brief",
                notes="Test notes",
                style="professional",
                tone="concise",
                audience="stakeholders",
                client_id="test_client",
            )

        assert result["status"] == "success"
        assert "enhanced_presentation.pptx" in result["path"]
        assert result["slides"] == 1
        assert result["client_id"] == "test_client"
        assert result["style"] == "professional"
        assert result["tone"] == "concise"
        assert result["audience"] == "stakeholders"
        assert "enhancement_methods" in result

    @pytest.mark.asyncio
    @patch("mcp_server_openai.tools.enhanced_content_creator.MCPClient")
    async def test_create_enhanced_presentation_error(self, mock_client_class):
        """Test presentation creation with error."""
        # Mock MCP client that raises an exception
        mock_client = AsyncMock()
        mock_client.call_server.side_effect = Exception("Test error")
        mock_client_class.return_value = mock_client

        result = await create_enhanced_presentation(
            number_of_slides=3, brief="Test brief", notes="Test notes", client_id="test_client"
        )

        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert result["client_id"] == "test_client"


class TestIntegration:
    """Integration tests for the enhanced content creator."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test the complete workflow from request to outline."""
        # Test data
        brief = "AI Strategy Presentation"
        notes = "Market analysis\nTechnology trends\nImplementation roadmap"
        num_slides = 4

        # Create MCP client
        client = MCPClient()

        # Test planning
        plan = await client.call_server(
            "sequential_thinking", "plan_presentation", {"brief": brief, "notes": notes, "number_of_slides": num_slides}
        )

        assert "slides" in plan
        assert len(plan["slides"]) >= num_slides

        # Test content enhancement
        enhanced = await client.call_server("brave_search", "search_content", {"query": f"{brief} {notes}"})

        assert "search_results" in enhanced

        # Test content generation
        slides = []
        for slide_info in plan["slides"]:
            content = await client.call_server("memory", "generate_content", {"slide_info": slide_info})
            slides.append(content)

        assert len(slides) == len(plan["slides"])

        # Test outline conversion
        outline = _convert_to_outline(plan, slides, enhanced)

        assert len(outline) == len(plan["slides"])
        assert all(isinstance(slide, tuple) for slide in outline)
        assert all(len(slide) == 2 for slide in outline)
        assert all(isinstance(slide[0], str) for slide in outline)
        assert all(isinstance(slide[1], list) for slide in outline)
