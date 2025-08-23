"""
Enhanced Icon Generation Tool

This tool provides intelligent icon generation and selection capabilities for various
content types including business, technology, creative, and educational themes. It
supports multiple styles and output formats with smart content matching.
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
DEFAULT_ICON_STYLE = "flat"
DEFAULT_ICON_FORMAT = "svg"
DEFAULT_ICON_SIZE = "medium"
DEFAULT_COLOR_SCHEME = "auto"

# Icon style options
ICON_STYLES = ["flat", "3d", "outline", "filled", "gradient", "minimalist"]
ICON_FORMATS = ["svg", "png", "ico", "webp"]
ICON_SIZES = ["small", "medium", "large", "custom"]


@dataclass
class IconRequest:
    """Request for icon generation/selection."""

    description: str
    count: int = 1
    content_type: str = "presentation"  # presentation, document, html, pdf
    style: str = DEFAULT_ICON_STYLE
    format: str = DEFAULT_ICON_FORMAT
    size: str = DEFAULT_ICON_SIZE
    color_scheme: str = DEFAULT_COLOR_SCHEME
    custom_width: int | None = None
    custom_height: int | None = None
    theme: str = "auto"  # auto, business, technology, creative, educational
    client_id: str | None = None


@dataclass
class IconResult:
    """Result from icon generation/selection."""

    url: str
    provider: str
    title: str
    description: str
    style: str
    format: str
    width: int
    height: int
    size_bytes: int
    color_scheme: str
    theme: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IconResponse:
    """Response containing icon generation results."""

    icons: list[IconResult]
    total_count: int
    provider_used: str
    fallback_used: bool
    processing_time: float
    status: str = "success"
    error_message: str | None = None


class IconifyAPIClient:
    """Client for Iconify API integration."""

    def __init__(self) -> None:
        self.base_url = "https://api.iconify.design"
        self.headers = {"Accept": "application/json", "User-Agent": "Enhanced-Icon-Generator/1.0"}

    async def search_icons(self, query: str, count: int = 1, style: str = "flat") -> list[IconResult]:
        """Search for icons using Iconify API."""
        async with httpx.AsyncClient(timeout=30) as client:
            # Search for icons
            search_params = {"query": query, "limit": min(count, 50)}

            try:
                response = await client.get(f"{self.base_url}/search", headers=self.headers, params=search_params)
                response.raise_for_status()

                data = response.json()
                results = []

                for icon in data.get("icons", [])[:count]:
                    icon_result = IconResult(
                        url=f"{self.base_url}/icon/{icon['prefix']}/{icon['name']}",
                        provider="iconify",
                        title=icon.get("name", query),
                        description=f"Icon: {icon.get('name', query)}",
                        style=style,
                        format="svg",
                        width=24,
                        height=24,
                        size_bytes=0,
                        color_scheme="auto",
                        theme="auto",
                        tags=icon.get("tags", []),
                        metadata={
                            "prefix": icon.get("prefix"),
                            "name": icon.get("name"),
                            "category": icon.get("category", ""),
                            "tags": icon.get("tags", []),
                        },
                    )
                    results.append(icon_result)

                return results

            except Exception as e:
                logger.warning(f"Iconify API search failed: {e}")
                return []


class LucideIconClient:
    """Client for Lucide icon integration."""

    def __init__(self) -> None:
        self.base_url = "https://lucide.dev/api/icons"
        self.headers = {"Accept": "application/json", "User-Agent": "Enhanced-Icon-Generator/1.0"}

    async def search_icons(self, query: str, count: int = 1, style: str = "outline") -> list[IconResult]:
        """Search for icons using Lucide API."""
        async with httpx.AsyncClient(timeout=30):
            try:
                # Lucide doesn't have a search API, so we'll use a predefined set of common icons
                # and filter based on the query
                common_icons = [
                    "home",
                    "user",
                    "settings",
                    "search",
                    "menu",
                    "close",
                    "plus",
                    "minus",
                    "edit",
                    "delete",
                    "save",
                    "download",
                    "upload",
                    "share",
                    "like",
                    "star",
                    "heart",
                    "eye",
                    "eye-off",
                    "lock",
                    "unlock",
                    "key",
                    "mail",
                    "phone",
                    "calendar",
                    "clock",
                    "map",
                    "location",
                    "link",
                    "external-link",
                    "arrow-right",
                    "arrow-left",
                    "arrow-up",
                    "arrow-down",
                    "chevron-right",
                    "chevron-left",
                    "check",
                    "x",
                    "alert-circle",
                    "info",
                    "help-circle",
                    "zap",
                    "sun",
                    "moon",
                ]

                # Filter icons based on query
                matching_icons = [icon for icon in common_icons if query.lower() in icon.lower()]

                if not matching_icons:
                    # Fallback to common icons if no match
                    matching_icons = common_icons[:count]

                results = []
                for icon_name in matching_icons[:count]:
                    icon_result = IconResult(
                        url=f"https://lucide.dev/api/icons/{icon_name}",
                        provider="lucide",
                        title=icon_name,
                        description=f"Lucide icon: {icon_name}",
                        style=style,
                        format="svg",
                        width=24,
                        height=24,
                        size_bytes=0,
                        color_scheme="auto",
                        theme="auto",
                        tags=[icon_name, "lucide"],
                        metadata={
                            "name": icon_name,
                            "category": "common",
                            "tags": [icon_name, "lucide"],
                        },
                    )
                    results.append(icon_result)

                return results

            except Exception as e:
                logger.warning(f"Lucide icon selection failed: {e}")
                return []


class CustomIconGenerator:
    """Client for custom icon generation."""

    def __init__(self) -> None:
        self.api_key = os.getenv("CUSTOM_ICON_API_KEY")
        self.base_url = os.getenv("CUSTOM_ICON_API_URL", "https://api.custom-icon.com")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def generate_icon(
        self, description: str, style: str = "flat", format: str = "svg", width: int = 64, height: int = 64
    ) -> list[IconResult]:
        """Generate custom icons using AI."""
        if not self.api_key:
            raise ValueError("CUSTOM_ICON_API_KEY not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "prompt": description,
                "style": style,
                "format": format,
                "width": width,
                "height": height,
                "count": 1,
            }

            try:
                response = await client.post(f"{self.base_url}/v1/generate", headers=self.headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results = []

                for artifact in data.get("artifacts", []):
                    icon_result = IconResult(
                        url=f"data:image/{format};base64,{artifact.get('base64', '')}",
                        provider="custom_ai",
                        title=f"AI Generated: {description}",
                        description=f"AI-generated icon based on: {description}",
                        style=style,
                        format=format,
                        width=width,
                        height=height,
                        size_bytes=len(artifact.get("base64", "")),
                        color_scheme="auto",
                        theme="auto",
                        tags=["ai-generated", "custom"],
                        metadata={
                            "prompt": description,
                            "style": style,
                            "format": format,
                            "seed": artifact.get("seed"),
                        },
                    )
                    results.append(icon_result)

                return results

            except Exception as e:
                logger.warning(f"Custom icon generation failed: {e}")
                return []


class EnhancedIconGenerator:
    """Main class for enhanced icon generation and selection."""

    def __init__(self) -> None:
        self.iconify_client = IconifyAPIClient()
        self.lucide_client = LucideIconClient()
        self.custom_client = CustomIconGenerator()
        self.provider_status = {"iconify": True, "lucide": True, "custom_ai": True}

    async def generate_icons(self, request: IconRequest) -> IconResponse:
        """Generate or select icons based on the request."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Try providers in priority order
            providers = ["custom_ai", "iconify", "lucide"]

            for provider in providers:
                if not self.provider_status.get(provider, True):
                    continue

                try:
                    if provider == "custom_ai":
                        icons = await self.custom_client.generate_icon(
                            request.description,
                            request.style,
                            request.format,
                            request.custom_width or 64,
                            request.custom_height or 64,
                        )
                    elif provider == "iconify":
                        icons = await self.iconify_client.search_icons(
                            request.description, request.count, request.style
                        )
                    elif provider == "lucide":
                        icons = await self.lucide_client.search_icons(request.description, request.count, request.style)
                    else:
                        continue

                    if icons:
                        processing_time = asyncio.get_event_loop().time() - start_time
                        return IconResponse(
                            icons=icons[: request.count],
                            total_count=len(icons),
                            provider_used=provider,
                            fallback_used=False,
                            processing_time=processing_time,
                        )

                except Exception as e:
                    logger.warning(f"Provider {provider} failed: {e}")
                    self.provider_status[provider] = False
                    continue

            # If all providers failed, return error
            processing_time = asyncio.get_event_loop().time() - start_time
            return IconResponse(
                icons=[],
                total_count=0,
                provider_used="none",
                fallback_used=True,
                processing_time=processing_time,
                status="error",
                error_message="All icon providers failed",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Icon generation failed: {e}")
            return IconResponse(
                icons=[],
                total_count=0,
                provider_used="none",
                fallback_used=True,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    async def get_content_aware_icons(self, content: str, content_type: str, count: int = 3) -> IconResponse:
        """Get icons that are contextually relevant to the content."""
        # Analyze content and generate appropriate icon description
        icon_description = self._generate_icon_description(content, content_type)

        request = IconRequest(
            description=icon_description,
            content_type=content_type,
            count=count,
            style="flat" if content_type in ["presentation", "document"] else "creative",
            theme=self._detect_theme(content),
        )

        return await self.generate_icons(request)

    def _generate_icon_description(self, content: str, content_type: str) -> str:
        """Generate an icon description based on content and type."""
        # Simple keyword extraction - in production, use NLP
        keywords = content.lower().split()[:5]
        filtered_keywords = [word for word in keywords if len(word) > 3]

        if not filtered_keywords:
            return content_type

        # Add content type context
        if content_type == "presentation":
            return f"{' '.join(filtered_keywords[:3])} presentation icon"
        elif content_type == "document":
            return f"{' '.join(filtered_keywords[:3])} document icon"
        elif content_type == "html":
            return f"{' '.join(filtered_keywords[:3])} web icon"
        else:
            return f"{' '.join(filtered_keywords[:3])} icon"

    def _detect_theme(self, content: str) -> str:
        """Detect the theme of the content for icon selection."""
        content_lower = content.lower()

        if any(word in content_lower for word in ["business", "finance", "corporate", "management"]):
            return "business"
        elif any(word in content_lower for word in ["technology", "digital", "software", "computer"]):
            return "technology"
        elif any(word in content_lower for word in ["creative", "art", "design", "innovation"]):
            return "creative"
        elif any(word in content_lower for word in ["education", "learning", "training", "knowledge"]):
            return "educational"
        else:
            return "auto"

    async def get_icon_suggestions(self, content: str, content_type: str) -> list[str]:
        """Get icon suggestions based on content analysis."""
        themes = self._detect_theme(content)

        # Icon suggestions based on theme
        icon_suggestions = {
            "business": ["📊", "📈", "💼", "🏢", "💰", "📋", "🎯", "📱"],
            "technology": ["💻", "🔧", "⚡", "🌐", "📱", "🔒", "📡", "💾"],
            "creative": ["🎨", "✨", "🌟", "🎭", "🎪", "🎨", "🎬", "🎵"],
            "educational": ["📚", "🎓", "✏️", "🔬", "🧪", "📝", "🎯", "💡"],
        }

        return icon_suggestions.get(themes, icon_suggestions["business"])


# Global instance
_icon_generator = EnhancedIconGenerator()


async def generate_icons(
    description: str,
    content_type: str = "presentation",
    style: str = "flat",
    format: str = "svg",
    size: str = "medium",
    color_scheme: str = "auto",
    theme: str = "auto",
    count: int = 1,
    client_id: str | None = None,
) -> IconResponse:
    """Generate or select icons based on the request."""
    request = IconRequest(
        description=description,
        content_type=content_type,
        style=style,
        format=format,
        size=size,
        color_scheme=color_scheme,
        theme=theme,
        count=count,
        client_id=client_id,
    )

    return await _icon_generator.generate_icons(request)


async def get_content_aware_icons(
    content: str, content_type: str = "presentation", count: int = 3, client_id: str | None = None
) -> IconResponse:
    """Get icons that are contextually relevant to the content."""
    return await _icon_generator.get_content_aware_icons(content, content_type, count)


async def get_icon_suggestions(
    content: str, content_type: str = "presentation", client_id: str | None = None
) -> list[str]:
    """Get icon suggestions based on content analysis."""
    return await _icon_generator.get_icon_suggestions(content, content_type)


def register(mcp) -> None:
    """Register the enhanced icon generation tools with the MCP server."""

    @mcp.tool()
    async def enhanced_icon_generate(
        description: str,
        content_type: str = "presentation",
        style: str = "flat",
        format: str = "svg",
        size: str = "medium",
        color_scheme: str = "auto",
        theme: str = "auto",
        count: int = 1,
        client_id: str | None = None,
    ) -> str:
        """Generate or select icons using multiple providers with smart content matching."""
        try:
            result = await generate_icons(
                description=description,
                content_type=content_type,
                style=style,
                format=format,
                size=size,
                color_scheme=color_scheme,
                theme=theme,
                count=count,
                client_id=client_id,
            )

            return json.dumps(
                {
                    "status": result.status,
                    "icons": [
                        {
                            "url": icon.url,
                            "provider": icon.provider,
                            "title": icon.title,
                            "description": icon.description,
                            "style": icon.style,
                            "format": icon.format,
                            "width": icon.width,
                            "height": icon.height,
                            "color_scheme": icon.color_scheme,
                            "theme": icon.theme,
                            "tags": icon.tags,
                        }
                        for icon in result.icons
                    ],
                    "provider_used": result.provider_used,
                    "fallback_used": result.fallback_used,
                    "processing_time": result.processing_time,
                    "total_count": result.total_count,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Enhanced icon generation failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "icons": [], "total_count": 0}, indent=2)

    @mcp.tool()
    async def enhanced_icon_content_aware(
        content: str, content_type: str = "presentation", count: int = 3, client_id: str | None = None
    ) -> str:
        """Get icons that are contextually relevant to the provided content."""
        try:
            result = await get_content_aware_icons(
                content=content, content_type=content_type, count=count, client_id=client_id
            )

            return json.dumps(
                {
                    "status": result.status,
                    "icons": [
                        {
                            "url": icon.url,
                            "provider": icon.provider,
                            "title": icon.title,
                            "description": icon.description,
                            "style": icon.style,
                            "format": icon.format,
                            "width": icon.width,
                            "height": icon.height,
                            "color_scheme": icon.color_scheme,
                            "theme": icon.theme,
                            "tags": icon.tags,
                        }
                        for icon in result.icons
                    ],
                    "provider_used": result.provider_used,
                    "fallback_used": result.fallback_used,
                    "processing_time": result.processing_time,
                    "total_count": result.total_count,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Content-aware icon generation failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "icons": [], "total_count": 0}, indent=2)

    @mcp.tool()
    async def enhanced_icon_suggestions(
        content: str, content_type: str = "presentation", client_id: str | None = None
    ) -> str:
        """Get icon suggestions based on content analysis."""
        try:
            suggestions = await get_icon_suggestions(content=content, content_type=content_type, client_id=client_id)

            return json.dumps(
                {
                    "status": "success",
                    "suggestions": suggestions,
                    "content_type": content_type,
                    "theme": "auto-detected",
                    "count": len(suggestions),
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Icon suggestions failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "suggestions": [], "count": 0}, indent=2)
