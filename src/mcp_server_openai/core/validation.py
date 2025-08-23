"""
Request validation models using Pydantic for consistent input validation.

This module provides validated request models for all API endpoints to ensure
data integrity and provide clear error messages for invalid inputs.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class OutputFormat(str, Enum):
    """Supported output formats."""

    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    LATEX = "latex"
    RTF = "rtf"
    PPTX = "pptx"
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    SVG = "svg"


class ContentStyle(str, Enum):
    """Content style options."""

    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMALIST = "minimalist"
    ACADEMIC = "academic"
    CORPORATE = "corporate"


class ImageStyle(str, Enum):
    """Image style options."""

    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMALIST = "minimalist"
    ARTISTIC = "artistic"
    REALISTIC = "realistic"


class IconStyle(str, Enum):
    """Icon style options."""

    OUTLINE = "outline"
    FILLED = "filled"
    DUOTONE = "duotone"
    SOLID = "solid"


class PPTRequest(BaseModel):
    """Validated PPT generation request."""

    notes: list[str] = Field(..., min_items=1, max_items=20, description="Slide content notes")
    brief: str = Field(..., min_length=10, max_length=1000, description="Presentation brief")
    target_length: str = Field("5-7 slides", description="Target presentation length")
    template_preference: ContentStyle = Field(ContentStyle.PROFESSIONAL, description="Template style")
    include_images: bool = Field(True, description="Include AI-generated images")
    include_icons: bool = Field(True, description="Include matching icons")
    language: str = Field("en", description="Content language")

    @validator("notes")
    def validate_notes(cls, v: list[str]) -> list[str]:
        """Validate notes content."""
        if not v:
            raise ValueError("Notes cannot be empty")

        for i, note in enumerate(v):
            if not note.strip():
                raise ValueError(f"Note {i+1} cannot be empty")
            if len(note) > 500:
                raise ValueError(f"Note {i+1} is too long (max 500 characters)")

        return v

    @validator("brief")
    def validate_brief(cls, v: str) -> str:
        """Validate brief content."""
        if not v.strip():
            raise ValueError("Brief cannot be empty")
        return v.strip()


class DocumentRequest(BaseModel):
    """Validated document generation request."""

    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    content: str = Field(..., min_length=10, description="Document content in Markdown")
    output_format: OutputFormat = Field(OutputFormat.PDF, description="Output format")
    template: ContentStyle = Field(ContentStyle.PROFESSIONAL, description="Document template")
    include_toc: bool = Field(True, description="Include table of contents")
    include_images: bool = Field(False, description="Process and include images")
    language: str = Field("en", description="Content language")

    @validator("content")
    def validate_content(cls, v: str) -> str:
        """Validate content."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > 100000:  # 100KB limit
            raise ValueError("Content is too long (max 100KB)")
        return v.strip()


class ImageRequest(BaseModel):
    """Validated image generation request."""

    query: str = Field(..., min_length=3, max_length=200, description="Image search query")
    style: ImageStyle = Field(ImageStyle.PROFESSIONAL, description="Image style")
    format: OutputFormat = Field(OutputFormat.JPEG, description="Image format")
    count: int = Field(1, ge=1, le=5, description="Number of images to generate")
    width: int | None = Field(None, ge=100, le=2048, description="Image width")
    height: int | None = Field(None, ge=100, le=2048, description="Image height")
    content_type: str = Field("general", description="Content type context")

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate search query."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class IconRequest(BaseModel):
    """Validated icon generation request."""

    query: str = Field(..., min_length=2, max_length=100, description="Icon search query")
    style: IconStyle = Field(IconStyle.OUTLINE, description="Icon style")
    size: str = Field("medium", description="Icon size (small, medium, large)")
    format: OutputFormat = Field(OutputFormat.SVG, description="Icon format")
    color: str | None = Field(None, description="Icon color (hex code)")
    provider: str = Field("lucide", description="Icon provider")

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate search query."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @validator("color")
    def validate_color(cls, v: str | None) -> str | None:
        """Validate color format."""
        if v is None:
            return v

        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")

        try:
            int(v[1:], 16)
        except ValueError as e:
            raise ValueError("Color must be a valid hex code") from e

        return v


class UnifiedContentRequest(BaseModel):
    """Validated unified content creation request."""

    title: str = Field(..., min_length=1, max_length=200, description="Content title")
    brief: str = Field(..., min_length=10, max_length=1000, description="Content brief")
    notes: list[str] = Field(..., min_items=1, max_items=20, description="Content points")
    output_format: OutputFormat = Field(OutputFormat.HTML, description="Primary output format")
    content_style: ContentStyle = Field(ContentStyle.PROFESSIONAL, description="Content style")
    include_images: bool = Field(True, description="Include AI-generated images")
    include_icons: bool = Field(True, description="Include matching icons")
    include_research: bool = Field(True, description="Include web research")
    target_audience: str = Field("General", description="Target audience")
    language: str = Field("en", description="Content language")

    @validator("notes")
    def validate_notes(cls, v: list[str]) -> list[str]:
        """Validate notes content."""
        if not v:
            raise ValueError("Notes cannot be empty")

        for i, note in enumerate(v):
            if not note.strip():
                raise ValueError(f"Note {i+1} cannot be empty")

        return v


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    timestamp: str = Field(..., description="Response timestamp")
    status: str = Field(..., description="Health status")
    uptime: float = Field(..., description="Server uptime in seconds")
    checks: dict[str, Any] = Field(..., description="Individual health checks")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: dict[str, Any] = Field(..., description="Error details")

    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters",
                    "details": {"field": "notes"},
                    "error_id": "uuid-here",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response model."""

    status: str = Field("success", description="Response status")
    data: dict[str, Any] = Field(..., description="Response data")
    message: str | None = Field(None, description="Optional message")
    timestamp: str = Field(..., description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {"file_path": "/output/generated_file.pptx", "file_size": "2.1MB", "generation_time": "12.3s"},
                "message": "Content generated successfully",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }
