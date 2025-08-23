"""
Request handlers for API endpoints.

This module contains refactored request handling logic to improve maintainability
and reduce complexity in the main streaming_http.py file.
"""

from typing import Any

from fastapi import Request
from fastapi.responses import Response

from ..core.error_handler import ValidationError, create_error_response
from ..core.logging import get_logger
from ..core.validation import (
    DocumentRequest,
    IconRequest,
    ImageRequest,
    PPTRequest,
    UnifiedContentRequest,
)
from .response_formatters import StreamingJSONResponse

logger = get_logger("request_handlers")


class RequestParser:
    """Utility class for parsing and validating requests."""

    @staticmethod
    async def parse_json_body(request: Request) -> dict[str, Any]:
        """Parse JSON body from request with error handling."""
        try:
            return await request.json()
        except Exception as e:
            logger.error("Failed to parse JSON body", error=e)
            raise ValidationError("Invalid JSON in request body") from e

    @staticmethod
    def validate_required_fields(body: dict[str, Any], required_fields: list[str]) -> None:
        """Validate that all required fields are present."""
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    @staticmethod
    def create_ppt_request(body: dict[str, Any]) -> PPTRequest:
        """Create and validate PPT request from body."""
        try:
            return PPTRequest(**body)
        except Exception as e:
            logger.error("PPT request validation failed", error=e)
            raise ValidationError(f"Invalid PPT request: {e}") from e

    @staticmethod
    def create_document_request(body: dict[str, Any]) -> DocumentRequest:
        """Create and validate document request from body."""
        try:
            return DocumentRequest(**body)
        except Exception as e:
            logger.error("Document request validation failed", error=e)
            raise ValidationError(f"Invalid document request: {e}") from e

    @staticmethod
    def create_image_request(body: dict[str, Any]) -> ImageRequest:
        """Create and validate image request from body."""
        try:
            return ImageRequest(**body)
        except Exception as e:
            logger.error("Image request validation failed", error=e)
            raise ValidationError(f"Invalid image request: {e}") from e

    @staticmethod
    def create_icon_request(body: dict[str, Any]) -> IconRequest:
        """Create and validate icon request from body."""
        try:
            return IconRequest(**body)
        except Exception as e:
            logger.error("Icon request validation failed", error=e)
            raise ValidationError(f"Invalid icon request: {e}") from e

    @staticmethod
    def create_unified_content_request(body: dict[str, Any]) -> UnifiedContentRequest:
        """Create and validate unified content request from body."""
        try:
            return UnifiedContentRequest(**body)
        except Exception as e:
            logger.error("Unified content request validation failed", error=e)
            raise ValidationError(f"Invalid unified content request: {e}") from e


class PPTRequestHandler:
    """Handler for PPT-related requests."""

    def __init__(self):
        self.logger = get_logger("ppt_handler")

    async def handle_generation(self, request: Request) -> Response:
        """Handle PPT generation request."""
        try:
            body = await RequestParser.parse_json_body(request)
            ppt_request = RequestParser.create_ppt_request(body)

            # Import here to avoid circular imports
            from ..tools.generators.enhanced_ppt_generator import create_enhanced_presentation

            self.logger.info(
                "Starting PPT generation", notes_count=len(ppt_request.notes), template=ppt_request.template_preference
            )

            result = await create_enhanced_presentation(
                notes=ppt_request.notes,
                brief=ppt_request.brief,
                target_length=ppt_request.target_length,
                template_preference=ppt_request.template_preference.value,
                include_images=ppt_request.include_images,
                include_icons=ppt_request.include_icons,
                language=ppt_request.language,
            )

            self.logger.info("PPT generation completed successfully")
            return StreamingJSONResponse(result.__dict__, status_code=200)

        except Exception as e:
            self.logger.error("PPT generation failed", error=e)
            return create_error_response(e, request)

    async def handle_analysis(self, request: Request) -> Response:
        """Handle PPT analysis request."""
        try:
            body = await RequestParser.parse_json_body(request)
            ppt_request = RequestParser.create_ppt_request(body)

            from ..tools.generators.enhanced_ppt_generator import EnhancedPPTGenerator

            self.logger.info("Starting PPT analysis", notes_count=len(ppt_request.notes))

            generator = EnhancedPPTGenerator()
            analysis = await generator.analyze_content(ppt_request)

            self.logger.info("PPT analysis completed successfully")
            return StreamingJSONResponse(analysis, status_code=200)

        except Exception as e:
            self.logger.error("PPT analysis failed", error=e)
            return create_error_response(e, request)


class DocumentRequestHandler:
    """Handler for document-related requests."""

    def __init__(self):
        self.logger = get_logger("document_handler")

    async def handle_generation(self, request: Request) -> Response:
        """Handle document generation request."""
        try:
            body = await RequestParser.parse_json_body(request)
            doc_request = RequestParser.create_document_request(body)

            from ..tools.generators.enhanced_document_generator import generate_document

            self.logger.info(
                "Starting document generation", format=doc_request.output_format, template=doc_request.template
            )

            result = await generate_document(
                title=doc_request.title,
                content=doc_request.content,
                output_format=doc_request.output_format.value,
                template=doc_request.template.value,
                include_toc=doc_request.include_toc,
                include_images=doc_request.include_images,
                language=doc_request.language,
            )

            self.logger.info("Document generation completed successfully")
            return StreamingJSONResponse(result.__dict__, status_code=200)

        except Exception as e:
            self.logger.error("Document generation failed", error=e)
            return create_error_response(e, request)


class ImageRequestHandler:
    """Handler for image-related requests."""

    def __init__(self):
        self.logger = get_logger("image_handler")

    async def handle_generation(self, request: Request) -> Response:
        """Handle image generation request."""
        try:
            body = await RequestParser.parse_json_body(request)
            image_request = RequestParser.create_image_request(body)

            from ..tools.generators.enhanced_image_generator import generate_image

            self.logger.info(
                "Starting image generation",
                query=image_request.query,
                style=image_request.style,
                count=image_request.count,
            )

            result = await generate_image(
                query=image_request.query,
                style=image_request.style.value,
                format=image_request.format.value,
                count=image_request.count,
                width=image_request.width,
                height=image_request.height,
                content_type=image_request.content_type,
            )

            self.logger.info("Image generation completed successfully")
            return StreamingJSONResponse(result.__dict__, status_code=200)

        except Exception as e:
            self.logger.error("Image generation failed", error=e)
            return create_error_response(e, request)


class IconRequestHandler:
    """Handler for icon-related requests."""

    def __init__(self):
        self.logger = get_logger("icon_handler")

    async def handle_generation(self, request: Request) -> Response:
        """Handle icon generation request."""
        try:
            body = await RequestParser.parse_json_body(request)
            icon_request = RequestParser.create_icon_request(body)

            from ..tools.generators.enhanced_icon_generator import generate_icon

            self.logger.info(
                "Starting icon generation",
                query=icon_request.query,
                style=icon_request.style,
                provider=icon_request.provider,
            )

            result = await generate_icon(
                query=icon_request.query,
                style=icon_request.style.value,
                size=icon_request.size,
                format=icon_request.format.value,
                color=icon_request.color,
                provider=icon_request.provider,
            )

            self.logger.info("Icon generation completed successfully")
            return StreamingJSONResponse(result.__dict__, status_code=200)

        except Exception as e:
            self.logger.error("Icon generation failed", error=e)
            return create_error_response(e, request)


class UnifiedContentRequestHandler:
    """Handler for unified content creation requests."""

    def __init__(self):
        self.logger = get_logger("unified_content_handler")

    async def handle_creation(self, request: Request) -> Response:
        """Handle unified content creation request."""
        try:
            body = await RequestParser.parse_json_body(request)
            content_request = RequestParser.create_unified_content_request(body)

            from ..tools.generators.unified_content_creator import create_unified_content

            self.logger.info(
                "Starting unified content creation",
                title=content_request.title,
                format=content_request.output_format,
                style=content_request.content_style,
            )

            result = await create_unified_content(
                title=content_request.title,
                brief=content_request.brief,
                notes=content_request.notes,
                output_format=content_request.output_format.value,
                content_style=content_request.content_style.value,
                include_images=content_request.include_images,
                include_icons=content_request.include_icons,
                include_research=content_request.include_research,
                target_audience=content_request.target_audience,
                language=content_request.language,
            )

            response_data = {
                "status": result.status,
                "title": result.title,
                "output_format": result.output_format,
                "file_path": result.file_path,
                "file_size": result.file_size,
                "sections_count": len(result.sections) if hasattr(result, "sections") else 0,
                "images_used": getattr(result, "images_used", 0),
                "icons_used": getattr(result, "icons_used", 0),
                "processing_time": getattr(result, "processing_time", 0),
                "error_message": getattr(result, "error_message", None),
            }

            self.logger.info("Unified content creation completed successfully")
            return StreamingJSONResponse(response_data, status_code=200)

        except Exception as e:
            self.logger.error("Unified content creation failed", error=e)
            return create_error_response(e, request)
