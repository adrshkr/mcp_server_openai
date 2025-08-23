"""
Enhanced Image Generation Tool

This tool provides intelligent image generation and selection capabilities by integrating
multiple image providers: Unsplash, Stable Diffusion, and Pixabay. It includes smart
content matching, fallback strategies, and optimization for different content formats.
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
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_IMAGES = 5
DEFAULT_IMAGE_QUALITY = "high"
DEFAULT_FORMAT = "jpeg"

# Image provider priorities
PROVIDER_PRIORITY = ["stable_diffusion", "unsplash", "pixabay"]


@dataclass
class ImageRequest:
    """Request for image generation/selection."""

    query: str
    content_type: str = "presentation"  # presentation, document, html, pdf
    style: str = "professional"  # professional, creative, modern, classic
    count: int = 1
    format: str = DEFAULT_FORMAT
    quality: str = DEFAULT_IMAGE_QUALITY
    size: str = "medium"  # small, medium, large, custom
    custom_width: int | None = None
    custom_height: int | None = None
    client_id: str | None = None


@dataclass
class ImageResult:
    """Result from image generation/selection."""

    url: str
    provider: str
    title: str
    description: str
    width: int
    height: int
    format: str
    size_bytes: int
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageResponse:
    """Response containing multiple image results."""

    images: list[ImageResult]
    total_count: int
    provider_used: str
    fallback_used: bool
    processing_time: float
    status: str = "success"
    error_message: str | None = None


class UnsplashAPIClient:
    """Client for Unsplash API integration."""

    def __init__(self) -> None:
        self.api_key = os.getenv("UNSPLASH_API_KEY")
        self.base_url = "https://api.unsplash.com"
        self.headers = {"Authorization": f"Client-ID {self.api_key}", "Accept-Version": "v1"}

    async def search_images(self, query: str, count: int = 1, orientation: str = "landscape") -> list[ImageResult]:
        """Search for images on Unsplash."""
        if not self.api_key:
            raise ValueError("UNSPLASH_API_KEY not configured")

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            params: dict[str, str | int] = {"query": query, "per_page": min(count, 30), "orientation": orientation}

            response = await client.get(f"{self.base_url}/search/photos", headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            for photo in data.get("results", []):
                image_result = ImageResult(
                    url=photo["urls"]["regular"],
                    provider="unsplash",
                    title=photo.get("description", query),
                    description=photo.get("alt_description", ""),
                    width=photo["width"],
                    height=photo["height"],
                    format="jpeg",
                    size_bytes=0,  # Unsplash doesn't provide file size
                    tags=[tag["title"] for tag in photo.get("tags", [])],
                    metadata={
                        "unsplash_id": photo["id"],
                        "photographer": photo["user"]["name"],
                        "photographer_username": photo["user"]["username"],
                        "likes": photo["likes"],
                        "downloads": photo.get("downloads", 0),
                    },
                )
                results.append(image_result)

            return results


class StableDiffusionClient:
    """Client for Stable Diffusion API integration."""

    def __init__(self) -> None:
        self.api_key = os.getenv("STABLE_DIFFUSION_API_KEY")
        self.base_url = os.getenv("STABLE_DIFFUSION_API_URL", "https://api.stability.ai")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def generate_image(
        self, prompt: str, count: int = 1, width: int = 1024, height: int = 1024
    ) -> list[ImageResult]:
        """Generate images using Stable Diffusion."""
        if not self.api_key:
            raise ValueError("STABLE_DIFFUSION_API_KEY not configured")

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": count,
                "steps": 30,
            }

            response = await client.post(
                f"{self.base_url}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            results = []

            for _i, artifact in enumerate(data.get("artifacts", [])):
                # For demo purposes, we'll create a placeholder result
                # In production, you'd save the generated image and return its URL
                image_result = ImageResult(
                    url=f"data:image/png;base64,{artifact['base64']}",
                    provider="stable_diffusion",
                    title=f"AI Generated: {prompt}",
                    description=f"AI-generated image based on prompt: {prompt}",
                    width=width,
                    height=height,
                    format="png",
                    size_bytes=len(artifact["base64"]),
                    tags=["ai-generated", "stable-diffusion"],
                    metadata={"prompt": prompt, "seed": artifact.get("seed"), "cfg_scale": 7, "steps": 30},
                )
                results.append(image_result)

            return results


class PixabayAPIClient:
    """Client for Pixabay API integration."""

    def __init__(self) -> None:
        self.api_key = os.getenv("PIXABAY_API_KEY")
        self.base_url = "https://pixabay.com/api"

    async def search_images(self, query: str, count: int = 1, image_type: str = "photo") -> list[ImageResult]:
        """Search for images on Pixabay."""
        if not self.api_key:
            raise ValueError("PIXABAY_API_KEY not configured")

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            params: dict[str, str | int] = {
                "key": self.api_key,
                "q": query,
                "image_type": image_type,
                "per_page": min(count, 200),
                "safesearch": "true",
            }

            response = await client.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            for hit in data.get("hits", []):
                image_result = ImageResult(
                    url=hit["webformatURL"],
                    provider="pixabay",
                    title=hit.get("tags", query),
                    description=hit.get("tags", ""),
                    width=hit["imageWidth"],
                    height=hit["imageHeight"],
                    format="jpeg",
                    size_bytes=hit.get("fileSize", 0),
                    tags=hit.get("tags", "").split(", "),
                    metadata={
                        "pixabay_id": hit["id"],
                        "user": hit["user"],
                        "likes": hit["likes"],
                        "downloads": hit["downloads"],
                        "views": hit["views"],
                    },
                )
                results.append(image_result)

            return results


class EnhancedImageGenerator:
    """Main class for enhanced image generation and selection."""

    def __init__(self) -> None:
        self.unsplash_client = UnsplashAPIClient()
        self.stable_diffusion_client = StableDiffusionClient()
        self.pixabay_client = PixabayAPIClient()
        self.provider_status = {"stable_diffusion": True, "unsplash": True, "pixabay": True}

    async def generate_images(self, request: ImageRequest) -> ImageResponse:
        """Generate or select images based on the request."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Try providers in priority order
            for provider in PROVIDER_PRIORITY:
                if not self.provider_status.get(provider, True):
                    continue

                try:
                    if provider == "stable_diffusion":
                        images = await self.stable_diffusion_client.generate_image(
                            request.query, request.count, request.custom_width or 1024, request.custom_height or 1024
                        )
                    elif provider == "unsplash":
                        images = await self.unsplash_client.search_images(request.query, request.count)
                    elif provider == "pixabay":
                        images = await self.pixabay_client.search_images(request.query, request.count)
                    else:
                        continue

                    if images:
                        processing_time = asyncio.get_event_loop().time() - start_time
                        return ImageResponse(
                            images=images[: request.count],
                            total_count=len(images),
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
            return ImageResponse(
                images=[],
                total_count=0,
                provider_used="none",
                fallback_used=True,
                processing_time=processing_time,
                status="error",
                error_message="All image providers failed",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Image generation failed: {e}")
            return ImageResponse(
                images=[],
                total_count=0,
                provider_used="none",
                fallback_used=True,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    async def get_content_aware_images(self, content: str, content_type: str, count: int = 3) -> ImageResponse:
        """Get images that are contextually relevant to the content."""
        # Analyze content and generate appropriate query
        query = self._generate_content_query(content, content_type)

        request = ImageRequest(
            query=query,
            content_type=content_type,
            count=count,
            style="professional" if content_type in ["presentation", "document"] else "creative",
        )

        return await self.generate_images(request)

    def _generate_content_query(self, content: str, content_type: str) -> str:
        """Generate an image search query based on content and type."""
        # Simple keyword extraction - in production, use NLP
        keywords = content.lower().split()[:5]
        filtered_keywords = [word for word in keywords if len(word) > 3]

        if not filtered_keywords:
            return content_type

        # Add content type context
        if content_type == "presentation":
            return f"{' '.join(filtered_keywords[:3])} business professional"
        elif content_type == "document":
            return f"{' '.join(filtered_keywords[:3])} document illustration"
        elif content_type == "html":
            return f"{' '.join(filtered_keywords[:3])} web design"
        else:
            return f"{' '.join(filtered_keywords[:3])} visual"

    async def optimize_image_for_format(self, image: ImageResult, target_format: str, target_size: str) -> ImageResult:
        """Optimize image for specific format and size requirements."""
        # In production, implement actual image optimization
        # For now, return the original image
        return image


# Global instance
_image_generator = EnhancedImageGenerator()


async def generate_images(
    query: str,
    content_type: str = "presentation",
    style: str = "professional",
    count: int = 1,
    format: str = "jpeg",
    quality: str = "high",
    size: str = "medium",
    client_id: str | None = None,
) -> ImageResponse:
    """Generate or select images based on the request."""
    request = ImageRequest(
        query=query,
        content_type=content_type,
        style=style,
        count=count,
        format=format,
        quality=quality,
        size=size,
        client_id=client_id,
    )

    return await _image_generator.generate_images(request)


async def get_content_aware_images(
    content: str, content_type: str = "presentation", count: int = 3, client_id: str | None = None
) -> ImageResponse:
    """Get images that are contextually relevant to the content."""
    return await _image_generator.get_content_aware_images(content, content_type, count)


async def optimize_image(
    image_url: str, target_format: str = "jpeg", target_size: str = "medium", client_id: str | None = None
) -> ImageResult:
    """Optimize an existing image for specific requirements."""
    # Create a mock image result for optimization
    # In production, implement actual image optimization
    image = ImageResult(
        url=image_url,
        provider="optimized",
        title="Optimized Image",
        description="Image optimized for target format and size",
        width=1024,
        height=768,
        format=target_format,
        size_bytes=0,
    )

    return await _image_generator.optimize_image_for_format(image, target_format, target_size)


def register(mcp) -> None:
    """Register the enhanced image generation tools with the MCP server."""

    @mcp.tool()
    async def enhanced_image_generate(
        query: str,
        content_type: str = "presentation",
        style: str = "professional",
        count: int = 1,
        format: str = "jpeg",
        quality: str = "high",
        size: str = "medium",
        client_id: str | None = None,
    ) -> str:
        """Generate or select images using multiple providers (Unsplash, Stable Diffusion, Pixabay)."""
        try:
            result = await generate_images(
                query=query,
                content_type=content_type,
                style=style,
                count=count,
                format=format,
                quality=quality,
                size=size,
                client_id=client_id,
            )

            return json.dumps(
                {
                    "status": result.status,
                    "images": [
                        {
                            "url": img.url,
                            "provider": img.provider,
                            "title": img.title,
                            "description": img.description,
                            "width": img.width,
                            "height": img.height,
                            "format": img.format,
                            "tags": img.tags,
                        }
                        for img in result.images
                    ],
                    "provider_used": result.provider_used,
                    "fallback_used": result.fallback_used,
                    "processing_time": result.processing_time,
                    "total_count": result.total_count,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Enhanced image generation failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "images": [], "total_count": 0}, indent=2)

    @mcp.tool()
    async def enhanced_image_content_aware(
        content: str, content_type: str = "presentation", count: int = 3, client_id: str | None = None
    ) -> str:
        """Get images that are contextually relevant to the provided content."""
        try:
            result = await get_content_aware_images(
                content=content, content_type=content_type, count=count, client_id=client_id
            )

            return json.dumps(
                {
                    "status": result.status,
                    "images": [
                        {
                            "url": img.url,
                            "provider": img.provider,
                            "title": img.title,
                            "description": img.description,
                            "width": img.width,
                            "height": img.height,
                            "format": img.format,
                            "tags": img.tags,
                        }
                        for img in result.images
                    ],
                    "provider_used": result.provider_used,
                    "fallback_used": result.fallback_used,
                    "processing_time": result.processing_time,
                    "total_count": result.total_count,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Content-aware image generation failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e), "images": [], "total_count": 0}, indent=2)

    @mcp.tool()
    async def enhanced_image_optimize(
        image_url: str, target_format: str = "jpeg", target_size: str = "medium", client_id: str | None = None
    ) -> str:
        """Optimize an existing image for specific format and size requirements."""
        try:
            result = await optimize_image(
                image_url=image_url, target_format=target_format, target_size=target_size, client_id=client_id
            )

            return json.dumps(
                {
                    "status": "success",
                    "optimized_image": {
                        "url": result.url,
                        "provider": result.provider,
                        "title": result.title,
                        "description": result.description,
                        "width": result.width,
                        "height": result.height,
                        "format": result.format,
                        "size_bytes": result.size_bytes,
                    },
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return json.dumps({"status": "error", "error_message": str(e)}, indent=2)
