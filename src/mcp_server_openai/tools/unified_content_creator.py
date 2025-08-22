"""
Unified Content Creator Tool

This tool provides a comprehensive content creation solution that integrates all MCP servers
to create high-quality content in multiple formats: PPT, DOC, PDF, and HTML. It leverages
sequential thinking for planning, brave search for research, memory for context management,
filesystem for organization, and enhanced image/icon generation for visual enhancement.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_OUTPUT_FORMAT = "presentation"
DEFAULT_CONTENT_STYLE = "professional"
DEFAULT_LANGUAGE = "English"
DEFAULT_THEME = "auto"

# Supported output formats
SUPPORTED_FORMATS = ["presentation", "document", "pdf", "html"]
CONTENT_STYLES = ["professional", "creative", "modern", "classic", "minimalist"]
LANGUAGES = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic"]


@dataclass
class ContentRequest:
    """Request for content creation."""

    title: str
    brief: str
    notes: list[str]
    output_format: str = DEFAULT_OUTPUT_FORMAT
    content_style: str = DEFAULT_CONTENT_STYLE
    language: str = DEFAULT_LANGUAGE
    theme: str = DEFAULT_THEME
    include_images: bool = True
    include_icons: bool = True
    target_length: str | None = None
    custom_template: str | None = None
    branding: dict[str, Any] | None = None
    client_id: str | None = None


@dataclass
class ContentOutline:
    """Structured content outline."""

    title: str
    sections: list[dict[str, Any]]
    total_sections: int
    estimated_length: str
    suggested_images: int
    suggested_icons: int
    themes: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentSection:
    """Individual content section."""

    title: str
    content: str
    section_type: str  # title, content, summary, etc.
    layout: str
    images: list[dict[str, Any]] = field(default_factory=list)
    icons: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentResult:
    """Result from content creation."""

    title: str
    output_format: str
    file_path: str
    file_size: int
    sections: list[ContentSection]
    images_used: int
    icons_used: int
    processing_time: float
    status: str = "success"
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MCPSequentialThinkingClient:
    """Client for MCP Sequential Thinking server."""

    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_SEQUENTIAL_THINKING_URL", "http://localhost:3001")
        self.headers = {"Content-Type": "application/json"}

    async def plan_content(self, title: str, brief: str, notes: list[str], output_format: str) -> ContentOutline:
        """Use sequential thinking to plan content structure."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "task": f"Plan content for {output_format} titled '{title}'",
                    "context": {"title": title, "brief": brief, "notes": notes, "format": output_format},
                    "steps": [
                        "Analyze the brief and notes",
                        "Determine optimal content structure",
                        "Plan sections and subsections",
                        "Suggest visual elements",
                        "Estimate content length",
                    ],
                }

                response = await client.post(f"{self.base_url}/think", headers=self.headers, json=payload)
                response.raise_for_status()

                data = response.json()

                # Parse the thinking result to create outline
                outline = self._parse_thinking_result(data, title, output_format)
                return outline

        except Exception as e:
            logger.warning(f"Sequential thinking failed: {e}")
            # Fallback to basic outline generation
            return self._generate_basic_outline(title, brief, notes, output_format)

    def _parse_thinking_result(self, data: dict[str, Any], title: str, output_format: str) -> ContentOutline:
        """Parse sequential thinking result into structured outline."""
        # In production, implement sophisticated parsing
        # For now, create a basic outline
        sections = [
            {"title": "Introduction", "type": "title", "content": "Brief overview"},
            {"title": "Main Content", "type": "content", "content": "Core information"},
            {"title": "Summary", "type": "summary", "content": "Key takeaways"},
        ]

        return ContentOutline(
            title=title,
            sections=sections,
            total_sections=len(sections),
            estimated_length="5-10 minutes",
            suggested_images=3,
            suggested_icons=2,
            themes=["professional", "informative"],
        )

    def _generate_basic_outline(self, title: str, brief: str, notes: list[str], output_format: str) -> ContentOutline:
        """Generate a basic outline when sequential thinking fails."""
        sections = [
            {"title": "Introduction", "type": "title", "content": brief},
            {"title": "Key Points", "type": "content", "content": "Main content from notes"},
            {"title": "Conclusion", "type": "summary", "content": "Summary and next steps"},
        ]

        return ContentOutline(
            title=title,
            sections=sections,
            total_sections=len(sections),
            estimated_length="5-10 minutes",
            suggested_images=2,
            suggested_icons=1,
            themes=["professional"],
        )


class MCPBraveSearchClient:
    """Client for MCP Brave Search server."""

    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_BRAVE_SEARCH_URL", "http://localhost:3002")
        self.headers = {"Content-Type": "application/json"}

    async def research_content(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Use Brave Search to research content topics."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"query": query, "max_results": max_results, "safe_search": True}

                response = await client.post(f"{self.base_url}/search", headers=self.headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results: list[dict[str, Any]] = data.get("results", [])
                return results

        except Exception as e:
            logger.warning(f"Brave search failed: {e}")
            return []


class MCPMemoryClient:
    """Client for MCP Memory server."""

    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_MEMORY_URL", "http://localhost:3003")
        self.headers = {"Content-Type": "application/json"}

    async def store_context(self, key: str, context: dict[str, Any]) -> bool:
        """Store context in memory."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"key": key, "context": context}

                response = await client.post(f"{self.base_url}/store", headers=self.headers, json=payload)
                response.raise_for_status()

                return True

        except Exception as e:
            logger.warning(f"Memory storage failed: {e}")
            return False

    async def retrieve_context(self, key: str) -> dict[str, Any] | None:
        """Retrieve context from memory."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.base_url}/retrieve/{key}", headers=self.headers)
                response.raise_for_status()

                data = response.json()
                return data.get("context")
            
        except Exception as e:
            logger.warning(f"Memory retrieval failed: {e}")
            return None


class MCPFilesystemClient:
    """Client for MCP Filesystem server."""

    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_FILESYSTEM_URL", "http://localhost:3004")
        self.headers = {"Content-Type": "application/json"}

    async def create_directory(self, path: str) -> bool:
        """Create directory in filesystem."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"path": path}

                response = await client.post(f"{self.base_url}/mkdir", headers=self.headers, json=payload)
                response.raise_for_status()

                return True

        except Exception as e:
            logger.warning(f"Directory creation failed: {e}")
            return False

    async def save_file(self, path: str, content: str) -> bool:
        """Save file to filesystem."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"path": path, "content": content}

                response = await client.post(f"{self.base_url}/write", headers=self.headers, json=payload)
                response.raise_for_status()

                return True

        except Exception as e:
            logger.warning(f"File save failed: {e}")
            return False


class UnifiedContentCreator:
    """Main unified content creator that orchestrates all MCP servers."""

    def __init__(self) -> None:
        self.sequential_thinking = MCPSequentialThinkingClient()
        self.brave_search = MCPBraveSearchClient()
        self.memory = MCPMemoryClient()
        self.filesystem = MCPFilesystemClient()

    async def create_content(self, request: ContentRequest) -> ContentResult:
        """Create unified content using all MCP servers."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Plan content using sequential thinking
            outline = await self.sequential_thinking.plan_content(
                request.title, request.brief, request.notes, request.output_format
            )

            # Step 2: Research content using Brave Search
            research_query = f"{request.title} {request.brief}"
            research_results = await self.brave_search.research_content(research_query)

            # Step 3: Generate content sections
            sections = await self._generate_content_sections(outline, research_results, request)

            # Step 4: Generate output file
            file_path, file_size = await self._generate_output_file(request, sections)

            # Step 5: Store context in memory
            if request.client_id:
                context = {
                    "title": request.title,
                    "output_format": request.output_format,
                    "file_path": file_path,
                    "sections": [s.__dict__ for s in sections],
                    "timestamp": asyncio.get_event_loop().time(),
                }
                await self.memory.store_context(f"content_{request.client_id}", context)

            processing_time = asyncio.get_event_loop().time() - start_time

            return ContentResult(
                title=request.title,
                output_format=request.output_format,
                file_path=file_path,
                file_size=file_size,
                sections=sections,
                images_used=sum(len(s.images) for s in sections),
                icons_used=sum(len(s.icons) for s in sections),
                processing_time=processing_time,
                status="success",
            )

        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            processing_time = asyncio.get_event_loop().time() - start_time

            return ContentResult(
                title=request.title,
                output_format=request.output_format,
                file_path="",
                file_size=0,
                sections=[],
                images_used=0,
                icons_used=0,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    async def _generate_content_sections(
        self, outline: ContentOutline, research_results: list[dict[str, Any]], request: ContentRequest
    ) -> list[ContentSection]:
        """Generate content sections based on outline and research."""
        sections = []

        for section_data in outline.sections:
            # Generate content for each section
            content = await self._generate_section_content(section_data, research_results, request)

            # Create section object
            section = ContentSection(
                title=section_data["title"],
                content=content,
                section_type=section_data.get("type", "content"),
                layout=section_data.get("layout", "default"),
            )

            # Add images and icons if requested
            if request.include_images:
                section.images = await self._generate_section_images(section_data, request)

            if request.include_icons:
                section.icons = await self._generate_section_icons(section_data, request)

            sections.append(section)

        return sections

    async def _generate_section_content(
        self, section_data: dict[str, Any], research_results: list[dict[str, Any]], request: ContentRequest
    ) -> str:
        """Generate content for a specific section."""
        # In production, use LLM for content generation
        # For now, create basic content based on notes and research

        base_content = section_data.get("content", "")

        # Enhance with research results
        if research_results:
            relevant_info = research_results[:2]  # Use first 2 research results
            enhanced_content = f"{base_content}" + "\n\nAdditional insights:\n"
            for result in relevant_info:
                enhanced_content += f"• {result.get('title', 'Research finding')}" + "\n"
        else:
            enhanced_content = base_content

        return enhanced_content

    async def _generate_section_images(
        self, section_data: dict[str, Any], request: ContentRequest
    ) -> list[dict[str, Any]]:
        """Generate images for a section using enhanced image generator."""
        try:
            from .enhanced_image_generator import generate_image

            # Generate relevant image for the section
            image_query = f"{section_data['title']} {request.content_style}"
            image_result = await generate_image(
                query=image_query,
                content_type="content",
                style=request.content_style,
                count=1,
                format="jpeg",
                quality="high",
                size="medium",
            )

            if image_result and hasattr(image_result, "url"):
                return [{"url": image_result.url, "provider": "unsplash", "title": section_data["title"]}]

                except Exception as e:
            logger.warning(f"Image generation failed for section {section_data['title']}: {e}")

        return []

    async def _generate_section_icons(
        self, section_data: dict[str, Any], request: ContentRequest
    ) -> list[dict[str, Any]]:
        """Generate icons for a section using enhanced icon generator."""
        try:
            from .enhanced_icon_generator import generate_icon

            # Generate relevant icon for the section
            icon_query = section_data["title"].lower()
            icon_result = await generate_icon(
                query=icon_query,
                style=request.content_style,
                size="small",
                provider="lucide",  # Default to Lucide for clean icons
            )

            if icon_result and hasattr(icon_result, "url"):
                return [{"url": icon_result.url, "provider": "lucide", "title": section_data["title"]}]

                except Exception as e:
            logger.warning(f"Icon generation failed for section {section_data['title']}: {e}")

        return []

    async def _generate_output_file(self, request: ContentRequest, sections: list[ContentSection]) -> tuple[str, int]:
        """Generate the final output file based on format."""
        output_dir = f"output/{request.output_format}s"
        await self.filesystem.create_directory(output_dir)

        if request.output_format == "presentation":
            return await self._generate_presentation(request, sections, output_dir)
        elif request.output_format == "document":
            return await self._generate_document(request, sections, output_dir)
        elif request.output_format == "pdf":
            return await self._generate_pdf(request, sections, output_dir)
        elif request.output_format == "html":
            return await self._generate_html(request, sections, output_dir)
        else:
            raise ValueError(f"Unsupported output format: {request.output_format}")

    async def _generate_presentation(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate PowerPoint presentation using enhanced PPT generator."""
        try:
            from .enhanced_ppt_generator import create_enhanced_presentation

            notes = [section.content for section in sections]
            result = await create_enhanced_presentation(
                notes=notes,
                    brief=request.brief,
                target_length=f"{len(sections)} slides",
                template_preference=request.content_style,
                    include_images=request.include_images,
                    language=request.language,
                client_id=request.client_id,
            )

            if hasattr(result, "file_path") and result.file_path:
                return result.file_path, result.file_size or 0
            else:
                # Fallback to basic presentation
                return await self._generate_basic_presentation(request, sections, output_dir)

        except Exception as e:
            logger.warning(f"Enhanced PPT generation failed: {e}")
            return await self._generate_basic_presentation(request, sections, output_dir)

    async def _generate_basic_presentation(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate basic presentation as fallback."""
        file_path = f"{output_dir}/{request.title.replace(' ', '_')}.pptx"

        # Create basic presentation content
        presentation_content = f"""
Title: {request.title}
Brief: {request.brief}

Sections:
{chr(10).join(f"- {section.title}: {section.content[:100]}..." for section in sections)}
        """.strip()

        await self.filesystem.save_file(file_path, presentation_content)
        return file_path, len(presentation_content.encode())

    async def _generate_document(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate Word document using enhanced document generator."""
        try:
            from .enhanced_document_generator import generate_document

            # Prepare content for document generation
            content = f"# {request.title}\n\n## Brief\n{request.brief}\n\n"
            for section in sections:
                content += f"## {section.title}\n{section.content}\n\n"

            result = await generate_document(
                content=content,
                output_format="docx",
                template="professional",
                language=request.language,
                custom_css=None,
            )

            if hasattr(result, "file_path") and result.file_path:
                return result.file_path, result.file_size or 0
            else:
                # Fallback to basic document
                return await self._generate_basic_document(request, sections, output_dir)

        except Exception as e:
            logger.warning(f"Enhanced document generation failed: {e}")
            return await self._generate_basic_document(request, sections, output_dir)

    async def _generate_basic_document(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate basic document as fallback."""
        file_path = f"{output_dir}/{request.title.replace(' ', '_')}.docx"

        document_content = f"""
# {request.title}

## Brief
{request.brief}

{chr(10).join(f"## {section.title}" + chr(10) + section.content + chr(10) for section in sections)}
        """.strip()

        await self.filesystem.save_file(file_path, document_content)
        return file_path, len(document_content.encode())

    async def _generate_pdf(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate PDF document using enhanced document generator."""
        try:
            from .enhanced_document_generator import generate_document

            # Prepare content for PDF generation
            content = f"# {request.title}\n\n## Brief\n{request.brief}\n\n"
            for section in sections:
                content += f"## {section.title}\n{section.content}\n\n"

            result = await generate_document(
                content=content,
                output_format="pdf",
                template="professional",
                language=request.language,
                custom_css=None,
            )

            if hasattr(result, "file_path") and result.file_path:
                return result.file_path, result.file_size or 0
            else:
                # Fallback to basic PDF
                return await self._generate_basic_pdf(request, sections, output_dir)

        except Exception as e:
            logger.warning(f"Enhanced PDF generation failed: {e}")
            return await self._generate_basic_pdf(request, sections, output_dir)

    async def _generate_basic_pdf(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate basic PDF as fallback."""
        file_path = f"{output_dir}/{request.title.replace(' ', '_')}.pdf"

        # For now, create text content that can be converted to PDF
        pdf_content = f"""
{request.title}
{'=' * len(request.title)}

Brief: {request.brief}

{chr(10).join(
    f"{section.title}" + chr(10) + "-" * len(section.title) + chr(10) + section.content + chr(10)
    for section in sections
)}
        """.strip()

        await self.filesystem.save_file(file_path, pdf_content)
        return file_path, len(pdf_content.encode())

    async def _generate_html(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate HTML document using enhanced document generator."""
        try:
            from .enhanced_document_generator import generate_document

            # Prepare content for HTML generation
            content = f"# {request.title}\n\n## Brief\n{request.brief}\n\n"
            for section in sections:
                content += f"## {section.title}\n{section.content}\n\n"

            result = await generate_document(
                title=request.title,
                content=content,
                output_format="html",
                template="professional",
                language=request.language,
                custom_css=None,
            )

            if hasattr(result, "file_path") and result.file_path:
                return result.file_path, result.file_size or 0
            else:
                # Fallback to basic HTML
                return await self._generate_basic_html(request, sections, output_dir)

        except Exception as e:
            logger.warning(f"Enhanced HTML generation failed: {e}")
            return await self._generate_basic_html(request, sections, output_dir)

    async def _generate_basic_html(
        self, request: ContentRequest, sections: list[ContentSection], output_dir: str
    ) -> tuple[str, int]:
        """Generate basic HTML as fallback."""
        file_path = f"{output_dir}/{request.title.replace(' ', '_')}.html"

        html_content = f"""
<!DOCTYPE html>
<html lang="{request.language.lower()}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{request.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .section {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>{request.title}</h1>
    <p><strong>Brief:</strong> {request.brief}</p>

    {chr(10).join(
        f'<div class="section"><h2>{section.title}</h2><p>{section.content}</p></div>'
        for section in sections
    )}
</body>
</html>
        """.strip()

        await self.filesystem.save_file(file_path, html_content)
        return file_path, len(html_content.encode())


# Global instance
_content_creator = UnifiedContentCreator()


async def create_unified_content(
    title: str,
    brief: str,
    notes: list[str],
    output_format: str = "presentation",
    content_style: str = "professional",
    language: str = "English",
    theme: str = "auto",
    include_images: bool = True,
    include_icons: bool = True,
    target_length: str | None = None,
    custom_template: str | None = None,
    branding: dict[str, Any] | None = None,
    client_id: str | None = None,
) -> ContentResult:
    """Create unified content using all MCP servers."""
    request = ContentRequest(
        title=title,
        brief=brief,
        notes=notes,
        output_format=output_format,
        content_style=content_style,
        language=language,
        theme=theme,
        include_images=include_images,
        include_icons=include_icons,
        target_length=target_length,
        custom_template=custom_template,
        branding=branding,
        client_id=client_id,
    )
    
    return await _content_creator.create_content(request)


def register(mcp) -> None:
    """Register the unified content creator tools with the MCP server."""
    
    @mcp.tool()
    async def unified_content_create(
        title: str,
        brief: str,
        notes: list[str],
        output_format: str = "presentation",
        content_style: str = "professional",
        language: str = "English",
        theme: str = "auto",
        include_images: bool = True,
        include_icons: bool = True,
        target_length: str | None = None,
        custom_template: str | None = None,
        branding: str | None = None,
        client_id: str | None = None,
    ) -> str:
        """Create unified content using all MCP servers with multiple output formats."""
        try:
            # Parse branding if provided as string
            branding_dict = None
            if branding:
                try:
                    branding_dict = json.loads(branding) if isinstance(branding, str) else branding
                except (json.JSONDecodeError, TypeError):
                    branding_dict = {"name": branding}

            result = await create_unified_content(
                title=title,
                brief=brief,
                notes=notes,
                output_format=output_format,
                content_style=content_style,
                language=language,
                theme=theme,
                include_images=include_images,
                include_icons=include_icons,
                target_length=target_length,
                custom_template=custom_template,
                branding=branding_dict,
                client_id=client_id,
            )

            return json.dumps(
                {
                    "status": result.status,
                    "title": result.title,
                "output_format": result.output_format,
                    "file_path": result.file_path,
                    "file_size": result.file_size,
                    "sections_count": len(result.sections),
                    "images_used": result.images_used,
                    "icons_used": result.icons_used,
                "processing_time": result.processing_time,
                "error_message": result.error_message,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Unified content creation failed: {e}")
            return json.dumps(
                {"status": "error", "error_message": str(e), "title": title, "output_format": output_format}, indent=2
            )
    
    @mcp.tool()
    async def unified_content_formats() -> str:
        """Get list of supported output formats and their capabilities."""
        formats_info = {
            "presentation": {
                "description": "PowerPoint presentation with enhanced visuals",
                "features": ["Slides", "Images", "Icons", "Templates", "Animations"],
                "best_for": ["Business presentations", "Educational content", "Sales pitches"],
            },
            "document": {
                "description": "Word document with rich formatting",
                "features": ["Text formatting", "Images", "Icons", "Tables", "Headers"],
                "best_for": ["Reports", "Proposals", "Documentation", "Manuals"],
                },
                "pdf": {
                "description": "Portable Document Format for sharing",
                "features": ["Fixed layout", "Images", "Icons", "Print-ready", "Universal"],
                "best_for": ["Final documents", "Print materials", "Archiving", "Sharing"],
                },
                "html": {
                "description": "Web-ready HTML with responsive design",
                "features": ["Web compatible", "Images", "Icons", "Responsive", "Interactive"],
                "best_for": ["Web content", "Email templates", "Digital publishing", "Online sharing"],
            },
        }

        return json.dumps(
            {
                "supported_formats": formats_info,
                "content_styles": CONTENT_STYLES,
                "languages": LANGUAGES,
                "capabilities": ["MCP Integration", "AI Planning", "Research", "Visual Enhancement"],
            },
            indent=2,
        )

    @mcp.tool()
    async def unified_content_status(client_id: str) -> str:
        """Get status of content creation for a specific client."""
        try:
            from .unified_content_creator import _content_creator

            # Retrieve context from memory
            context = await _content_creator.memory.retrieve_context(f"content_{client_id}")

            if context:
                return json.dumps({"status": "found", "client_id": client_id, "context": context}, indent=2)
            else:
                return json.dumps(
                    {
                        "status": "not_found",
                        "client_id": client_id,
                        "message": "No content creation context found for this client",
                    },
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "client_id": client_id}, indent=2)
