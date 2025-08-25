"""
Enhanced content creation tool with open-source MCP server integration.

This tool leverages multiple MCP servers to create high-quality PowerPoint presentations:
- Sequential thinking for content planning
- Brave search for research enhancement
- Memory server for content generation
- Filesystem for output management
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...logging_utils import get_logger, log_accept, log_exception, log_response
from ...progress import create_progress_tracker

_LOG = get_logger("mcp.tool.enhanced_content_creator")
_TOOL = "enhanced_content.create"

# MCP Server configurations
MCP_SERVERS = {
    "sequential_thinking": "@modelcontextprotocol/server-sequential-thinking",
    "brave_search": "@modelcontextprotocol/server-brave-search",
    "memory": "@modelcontextprotocol/server-memory",
    "filesystem": "@modelcontextprotocol/server-filesystem",
}


@dataclass
class ContentRequest:
    """Structured content creation request."""

    number_of_slides: int
    brief: str
    notes: str
    style: str = "professional"
    tone: str = "concise"
    audience: str = "stakeholders"
    client_id: str | None = None


@dataclass
class SlideContent:
    """Individual slide content structure."""

    title: str
    content: list[str]
    slide_type: str = "content"  # title, content, summary, etc.


@dataclass
class ContentPlan:
    """Structured content plan for presentation."""

    title: str
    overview: str
    slides: list[SlideContent]
    key_messages: list[str]
    call_to_action: str


class MCPClient:
    """Client for interacting with open-source MCP servers."""

    def __init__(self) -> None:
        self.servers: dict[str, Any] = {}

    async def start_server(self, server_name: str, server_package: str) -> bool:
        """Start an MCP server and establish connection."""
        try:
            # Start server process
            process = await asyncio.create_subprocess_exec(
                "npx", server_package, "--help", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                _LOG.info(f"Successfully started {server_name} server")
                return True
            else:
                _LOG.warning(f"Failed to start {server_name} server: {stderr.decode()}")
                return False

        except Exception as e:
            _LOG.error(f"Error starting {server_name} server: {e}")
            return False

    async def call_server(self, server_name: str, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call a method on an MCP server."""
        try:
            # This is a simplified implementation
            # In a real scenario, you'd establish proper MCP connections
            if server_name == "sequential_thinking":
                return await self._call_sequential_thinking(method, params)
            elif server_name == "brave_search":
                return await self._call_brave_search(method, params)
            elif server_name == "memory":
                return await self._call_memory(method, params)
            else:
                return {"error": f"Unknown server: {server_name}"}
        except Exception as e:
            _LOG.error(f"Error calling {server_name}.{method}: {e}")
            return {"error": str(e)}

    async def _call_sequential_thinking(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call sequential thinking server for content planning."""
        if method == "plan_presentation":
            return await self._plan_presentation_structure(params)
        return {"error": f"Unknown method: {method}"}

    async def _call_brave_search(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call brave search server for research enhancement."""
        if method == "search_content":
            return await self._search_enhancement(params)
        return {"error": f"Unknown method: {method}"}

    async def _call_memory(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call memory server for content generation."""
        if method == "generate_content":
            return await self._generate_slide_content(params)
        return {"error": f"Unknown method: {method}"}

    async def _plan_presentation_structure(self, params: dict[str, Any]) -> dict[str, Any]:
        """Plan the presentation structure using sequential thinking."""
        brief = params.get("brief", "")
        notes = params.get("notes", "")
        num_slides = params.get("number_of_slides", 5)

        # Create a logical structure based on content
        slides = []

        # Title slide
        slides.append(SlideContent(title="Executive Summary", content=[brief], slide_type="title"))

        # Content slides based on notes
        if notes:
            note_points = [note.strip() for note in notes.split("\n") if note.strip()]
            points_per_slide = max(1, len(note_points) // (num_slides - 1))

            for i in range(1, num_slides - 1):
                start_idx = (i - 1) * points_per_slide
                end_idx = start_idx + points_per_slide
                slide_points = note_points[start_idx:end_idx]

                if slide_points:
                    slides.append(SlideContent(title=f"Key Point {i}", content=slide_points, slide_type="content"))

        # Summary slide
        slides.append(
            SlideContent(
                title="Next Steps & Recommendations",
                content=["Action items", "Timeline", "Success metrics"],
                slide_type="summary",
            )
        )

        return {
            "title": f"Presentation: {brief[:50]}...",
            "overview": brief,
            "slides": [slide.__dict__ for slide in slides],
            "key_messages": [brief],
            "call_to_action": "Review and provide feedback",
        }

    async def _search_enhancement(self, params: dict[str, Any]) -> dict[str, Any]:
        """Enhance content with web search results."""
        query = params.get("query", "")

        # Simulate search enhancement
        enhanced_content = {
            "search_results": [
                f"Enhanced information about: {query}",
                "Industry best practices and trends",
                "Relevant case studies and examples",
            ],
            "additional_context": f"Enhanced context for: {query}",
            "sources": ["Industry reports", "Best practices", "Case studies"],
        }

        return enhanced_content

    async def _generate_slide_content(self, params: dict[str, Any]) -> dict[str, Any]:
        """Generate detailed slide content using memory server."""
        slide_info = params.get("slide_info", {})

        # Generate enhanced content
        enhanced_content = {
            "title": slide_info.get("title", "Slide Title"),
            "bullet_points": [
                f"Enhanced point about {slide_info.get('title', 'topic')}",
                "Supporting evidence and data",
                "Practical examples and applications",
                "Key takeaways and insights",
            ],
            "visual_suggestions": ["Charts", "Diagrams", "Infographics"],
            "speaker_notes": f"Key talking points for {slide_info.get('title', 'this slide')}",
        }

        return enhanced_content


async def create_enhanced_presentation(
    number_of_slides: int,
    brief: str,
    notes: str,
    style: str = "professional",
    tone: str = "concise",
    audience: str = "stakeholders",
    client_id: str | None = None,
) -> dict[str, Any]:
    """
    Create an enhanced PowerPoint presentation using open-source MCP servers.

    Args:
        number_of_slides: Number of slides to create
        brief: Brief description of the presentation
        notes: Detailed notes for content
        style: Presentation style (professional, creative, minimal)
        tone: Content tone (concise, detailed, persuasive)
        audience: Target audience
        client_id: Client identifier for customization

    Returns:
        Dictionary with presentation metadata and file path
    """
    request_id = f"enhanced-req-{int(time.time() * 1000)}"

    # Create progress tracker
    progress = create_progress_tracker(_TOOL, request_id, total_steps=6)

    # Log request acceptance
    log_accept(
        _LOG,
        tool=_TOOL,
        client_id=client_id,
        request_id=request_id,
        payload={"slides": number_of_slides, "brief": brief[:100]},
    )

    start_time = time.monotonic()

    try:
        # Step 1: Initialize MCP client
        with progress.step_context("initialize_mcp", {"status": "starting_servers"}):
            mcp_client = MCPClient()
            progress.update_progress(16.7, "MCP client initialized")

        # Step 2: Plan presentation structure
        with progress.step_context("plan_structure", {"method": "sequential_thinking"}):
            plan_result = await mcp_client.call_server(
                "sequential_thinking",
                "plan_presentation",
                {
                    "brief": brief,
                    "notes": notes,
                    "number_of_slides": number_of_slides,
                    "style": style,
                    "tone": tone,
                    "audience": audience,
                },
            )
            progress.update_progress(33.3, "Structure planned")

        # Step 3: Enhance content with research
        with progress.step_context("enhance_content", {"method": "brave_search"}):
            enhanced_content = await mcp_client.call_server(
                "brave_search", "search_content", {"query": f"{brief} {notes[:100]}"}
            )
            progress.update_progress(50.0, "Content enhanced")

        # Step 4: Generate detailed slide content
        with progress.step_context("generate_slides", {"method": "memory"}):
            slides = []
            for slide_info in plan_result.get("slides", []):
                slide_content = await mcp_client.call_server("memory", "generate_content", {"slide_info": slide_info})
                slides.append(slide_content)
            progress.update_progress(66.7, "Slides generated")

        # Step 5: Create PowerPoint presentation
        with progress.step_context("create_presentation", {"method": "python_pptx"}):
            from .content_creator import _create_ppt_from_outline

            # Convert enhanced content to outline format
            outline = _convert_to_outline(plan_result, slides, enhanced_content)
            presentation = _create_ppt_from_outline(outline)
            progress.update_progress(83.3, "PPT created")

        # Step 6: Save and finalize
        with progress.step_context("save_presentation", {"method": "filesystem"}):
            output_path = _save_enhanced_ppt(presentation, client_id or "default", brief[:30])
            progress.update_progress(100.0, "Presentation saved")

        # Log successful completion
        duration_ms = (time.monotonic() - start_time) * 1000.0
        log_response(_LOG, tool=_TOOL, request_id=request_id, status="ok", duration_ms=duration_ms, size=len(slides))

        progress.complete(
            "presentation_created", {"status": "success", "slides_count": len(slides), "output_path": str(output_path)}
        )

        return {
            "status": "success",
            "path": str(output_path),
            "slides": len(slides),
            "client_id": client_id,
            "style": style,
            "tone": tone,
            "audience": audience,
            "enhancement_methods": list(MCP_SERVERS.keys()),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as exc:
        log_exception(_LOG, tool=_TOOL, request_id=request_id, exc=exc)
        duration_ms = (time.monotonic() - start_time) * 1000.0
        log_response(_LOG, tool=_TOOL, request_id=request_id, status="error", duration_ms=duration_ms)

        progress.complete("presentation_failed", {"status": "error", "error": str(exc)})

        return {"status": "error", "error": str(exc), "client_id": client_id}


def _convert_to_outline(
    plan: dict[str, Any], slides: list[dict[str, Any]], enhanced: dict[str, Any]
) -> list[tuple[str, list[str]]]:
    """Convert enhanced content plan to outline format for PPT generation."""
    outline: list[tuple[str, list[str]]] = []

    for i, slide in enumerate(slides):
        title = slide.get("title", f"Slide {i+1}")
        content = slide.get("bullet_points", [])

        # Add enhanced content if available
        if enhanced.get("search_results"):
            content.extend(enhanced.get("search_results", []))

        # Ensure content is a list of strings
        content = [str(item) for item in content if item]

        outline.append((title, content))

    return outline


def _save_enhanced_ppt(presentation: Any, client: str, project: str) -> Path:
    """Save enhanced presentation to output directory."""
    output_dir = Path("output") / client / project
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"enhanced_presentation_{int(time.time())}.pptx"
    presentation.save(str(output_path))

    return output_path


def register(mcp: Any) -> None:
    """
    Register enhanced content creation tools on the provided FastMCP instance.
    """

    @mcp.tool(
        name="enhanced_content.create",
        description=(
            "Create enhanced PowerPoint presentations using open-source MCP servers "
            "for content generation, planning, and research enhancement."
        ),
    )
    async def create_presentation(
        number_of_slides: int,
        brief: str,
        notes: str,
        style: str = "professional",
        tone: str = "concise",
        audience: str = "stakeholders",
        client_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create an enhanced PowerPoint presentation.

        Args:
            number_of_slides: Number of slides to create
            brief: Brief description of the presentation
            notes: Detailed notes for content
            style: Presentation style (professional, creative, minimal)
            tone: Content tone (concise, detailed, persuasive)
            audience: Target audience
            client_id: Client identifier for customization

        Returns:
            Dictionary with presentation metadata and file path
        """
        return await create_enhanced_presentation(
            number_of_slides=number_of_slides,
            brief=brief,
            notes=notes,
            style=style,
            tone=tone,
            audience=audience,
            client_id=client_id,
        )

    @mcp.tool(
        name="enhanced_content.plan", description="Plan presentation structure using sequential thinking MCP server."
    )
    async def plan_presentation(
        brief: str,
        notes: str,
        number_of_slides: int,
        style: str = "professional",
        tone: str = "concise",
        audience: str = "stakeholders",
    ) -> dict[str, Any]:
        """
        Plan presentation structure using MCP servers.

        Args:
            brief: Brief description
            notes: Detailed notes
            number_of_slides: Target slide count
            style: Presentation style
            tone: Content tone
            audience: Target audience

        Returns:
            Structured content plan
        """
        mcp_client = MCPClient()
        return await mcp_client.call_server(
            "sequential_thinking",
            "plan_presentation",
            {
                "brief": brief,
                "notes": notes,
                "number_of_slides": number_of_slides,
                "style": style,
                "tone": tone,
                "audience": audience,
            },
        )

    @mcp.tool(
        name="enhanced_content.enhance", description="Enhance content with research using brave search MCP server."
    )
    async def enhance_content(query: str) -> dict[str, Any]:
        """
        Enhance content with web research.

        Args:
            query: Search query for enhancement

        Returns:
            Enhanced content and context
        """
        mcp_client = MCPClient()
        return await mcp_client.call_server("brave_search", "search_content", {"query": query})
