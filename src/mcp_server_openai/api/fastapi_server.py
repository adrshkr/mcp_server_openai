"""
Enhanced FastAPI server with comprehensive API documentation.

This module provides a FastAPI-based server with OpenAPI documentation,
request validation, and improved error handling.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from ..core.config import get_config
from ..core.error_handler import create_error_response, get_error_handler
from ..core.logging import get_logger
from ..core.validation import (
    DocumentRequest,
    ErrorResponse,
    HealthCheckResponse,
    IconRequest,
    ImageRequest,
    PPTRequest,
    SuccessResponse,
    UnifiedContentRequest,
)

# Request handlers not needed - using direct imports in endpoints

# Initialize core systems
config = get_config()
logger = get_logger("fastapi_server")
error_handler = get_error_handler()

# Request handlers not needed - using direct imports in endpoints


def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application with comprehensive documentation."""

    app = FastAPI(
        title="MCP Server OpenAI",
        description="""
        AI-powered content creation platform with comprehensive tools for generating
        presentations, documents, images, and icons.

        ## Features

        - **PowerPoint Generation**: Create professional presentations with AI content
        - **Document Generation**: Generate Word docs, PDFs, HTML with smart formatting
        - **Image Generation**: AI-generated images that match your content
        - **Icon Generation**: Create matching icons for your content
        - **Unified Content Creation**: Single API for all content types
        - **Research Integration**: Automatically enhance content with web research

        ## Authentication

        This API requires valid API keys for external services (OpenAI, etc.) to be
        configured in the server environment.

        ## Rate Limits

        - 100 requests per minute per client
        - Large content generation may take 30-60 seconds

        ## Support

        - Documentation: [GitHub Repository](https://github.com/adrshkr/mcp-server-openai)
        - Issues: [GitHub Issues](https://github.com/adrshkr/mcp-server-openai/issues)
        """,
        version="0.2.0",
        contact={
            "name": "MCP Server OpenAI Team",
            "url": "https://github.com/adrshkr/mcp-server-openai",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for consistent error responses."""
        return create_error_response(exc, request)

    return app


# Create FastAPI app instance
app = create_fastapi_app()


# NOTE: This FastAPI app is optional in this project (primary server uses streaming_http). Avoid
# double-decorating endpoints. The duplicate '@app.post(' above line was removed and this comment
# clarifies the intent.


# Health and monitoring endpoints
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Basic health check",
    description="Simple health check endpoint that returns server status.",
)
async def health_check():
    """Basic health check endpoint."""
    from ..health import health_checker

    result = await health_checker.basic_health_check()
    return result


@app.get(
    "/health/live",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Liveness probe",
    description="Liveness probe for container orchestration. Used to determine if container should be restarted.",
)
async def liveness_check():
    """Liveness probe endpoint."""
    from ..health import health_checker

    result = await health_checker.liveness_check()
    if result["status"] != "healthy":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.get(
    "/health/ready",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Readiness probe",
    description="Readiness probe for container orchestration. Used to determine if container can accept traffic.",
)
async def readiness_check():
    """Readiness probe endpoint."""
    from ..health import health_checker

    result = await health_checker.readiness_check()
    if result["status"] != "healthy":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.get(
    "/status",
    response_model=dict[str, Any],
    tags=["Health"],
    summary="Detailed status",
    description="Comprehensive system status with detailed diagnostics.",
)
async def detailed_status():
    """Detailed status endpoint."""
    from ..health import health_checker

    return await health_checker.detailed_status()


@app.get(
    "/info",
    response_model=dict[str, Any],
    tags=["Information"],
    summary="Service information",
    description="Service metadata, available endpoints, and feature flags.",
)
async def service_info():
    """Service information endpoint."""
    return {
        "service": "MCP Server OpenAI",
        "version": "0.2.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "endpoints": {
            "ppt_generation": "/api/v1/ppt/generate",
            "document_generation": "/api/v1/document/generate",
            "image_generation": "/api/v1/image/generate",
            "icon_generation": "/api/v1/icon/generate",
            "unified_content": "/api/v1/unified/create",
            "content_creation": "/api/v1/content/create",
            "voice_transcribe": "/api/v1/voice/transcribe",
            "voice_speak": "/api/v1/voice/speak",
            "voice_content": "/api/v1/voice/content",
        },
        "features": {
            "ppt_generation": config.features.enable_ppt_generation,
            "document_generation": config.features.enable_document_generation,
            "image_generation": config.features.enable_image_generation,
            "icon_generation": config.features.enable_icon_generation,
            "research_integration": config.features.enable_research,
            "voice_mode": config.features.enable_voice_mode,
            "caching": config.features.enable_caching,
            "monitoring": config.features.enable_monitoring,
        },
        "documentation": {
            "openapi": "/openapi.json",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
    }


# Content generation endpoints
@app.post(
    "/api/v1/ppt/generate",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Generate PowerPoint presentation",
    description="""
    Generate a professional PowerPoint presentation with AI-powered content,
    images, and icons based on your notes and brief.

    **Features:**
    - Multiple template styles (professional, creative, modern, etc.)
    - AI-generated content enhancement
    - Automatic image and icon integration
    - Support for multiple languages

    **Processing Time:** 30-60 seconds for typical presentations
    """,
)
async def generate_ppt(ppt_request: PPTRequest):
    """Generate PowerPoint presentation."""
    logger.info(
        "PPT generation request received", notes_count=len(ppt_request.notes), template=ppt_request.template_preference
    )

    try:
        # Import here to avoid circular imports
        from ..tools.generators.enhanced_ppt_generator import create_enhanced_presentation

        result = await create_enhanced_presentation(
            notes=ppt_request.notes,
            brief=ppt_request.brief,
            target_length=ppt_request.target_length,
            template_preference=ppt_request.template_preference.value,
            include_images=ppt_request.include_images,
            include_icons=ppt_request.include_icons,
            language=ppt_request.language,
        )

        logger.info("PPT generation completed successfully")
        return {"status": "success", "data": result.__dict__, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        logger.error("PPT generation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/document/generate",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Generate document",
    description="""
    Generate documents in multiple formats (PDF, DOCX, HTML, Markdown) with
    professional templates and smart formatting.

    **Supported Formats:**
    - PDF: Portable Document Format
    - DOCX: Microsoft Word document
    - HTML: Web-ready HTML with responsive design
    - Markdown: Simple, portable format

    **Processing Time:** 10-30 seconds depending on content length and format
    """,
)
async def generate_document(doc_request: DocumentRequest):
    """Generate document in specified format."""
    logger.info("Document generation request received", format=doc_request.output_format, template=doc_request.template)

    try:
        from ..tools.generators.enhanced_document_generator import generate_document as gen_doc

        result = await gen_doc(
            title=doc_request.title,
            content=doc_request.content,
            output_format=doc_request.output_format.value,
            template=doc_request.template.value,
            include_toc=doc_request.include_toc,
            language=doc_request.language,
        )

        logger.info("Document generation completed successfully")
        return {"status": "success", "data": result.__dict__, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        logger.error("Document generation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/image/generate",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Generate images",
    description="""
    Generate or find relevant images for your content using multiple providers
    including Unsplash, Stable Diffusion, and Pixabay.

    **Image Sources:**
    - Unsplash: High-quality stock photos
    - Stable Diffusion: AI-generated custom images
    - Pixabay: Additional stock photo library

    **Processing Time:** 5-15 seconds per image
    """,
)
async def generate_image(image_request: ImageRequest):
    """Generate or find relevant images."""
    logger.info(
        "Image generation request received",
        query=image_request.query,
        style=image_request.style,
        count=image_request.count,
    )

    try:
        from ..tools.generators.enhanced_image_generator import generate_images

        result = await generate_images(
            query=image_request.query,
            content_type=image_request.content_type,
            style=image_request.style.value,
            count=image_request.count,
            format=image_request.format.value,
            quality="high",
            size="medium",
        )

        logger.info("Image generation completed successfully")
        return {"status": "success", "data": result.__dict__, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        logger.error("Image generation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/icon/generate",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Generate icons",
    description="""
    Generate matching icons for your content using multiple icon providers
    including Iconify, Lucide, and custom AI generation.

    **Icon Providers:**
    - Lucide: Modern, consistent icons
    - Iconify: Extensive icon library
    - Custom AI: AI-generated custom icons

    **Processing Time:** 2-5 seconds per icon
    """,
)
async def generate_icon(icon_request: IconRequest):
    """Generate matching icons."""
    logger.info(
        "Icon generation request received",
        query=icon_request.query,
        style=icon_request.style,
        provider=icon_request.provider,
    )

    try:
        from ..tools.generators.enhanced_icon_generator import generate_icons

        result = await generate_icons(
            description=icon_request.query,
            content_type="presentation",
            style=icon_request.style.value,
            format=icon_request.format.value,
            size=icon_request.size,
            count=1,
        )

        logger.info("Icon generation completed successfully")
        return {"status": "success", "data": result.__dict__, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        logger.error("Icon generation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# Free Content Creation endpoint (LLM optional via env keys)
@app.post(
    "/api/v1/content/create",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Create content using free services",
)
async def create_free_content_endpoint(content_request: dict[str, Any]):
    """Create content using only free and open-source services."""
    try:
        from ..tools.generators.free_content_creator import create_content

        # Accept both 'prompt' and 'brief'
        prompt = content_request.get("prompt") or content_request.get("brief") or ""
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt or brief is required")

        result = await create_content(
            prompt=prompt,
            content_type=content_request.get("content_type", "article"),
            max_tokens=content_request.get("max_tokens", 2000),
            tone=content_request.get("tone", "professional"),
            audience=content_request.get("audience", "general"),
            include_research=content_request.get("include_research", True),
            language=content_request.get("language", "en"),
        )

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Free content creation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/unified/create",
    response_model=SuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Content Generation"],
    summary="Create unified content",
    description="""
    Create comprehensive content in multiple formats with AI-powered planning,
    research integration, and visual enhancement.

    **Features:**
    - AI-powered content planning and structuring
    - Automatic web research and fact-checking
    - Multi-format output (PPT, PDF, HTML, etc.)
    - Visual enhancement with images and icons
    - Content validation and optimization

    **Processing Time:** 60-120 seconds for comprehensive content creation
    """,
)
async def create_unified_content(content_request: UnifiedContentRequest):
    """Create unified content with comprehensive features."""
    logger.info(
        "Unified content creation request received",
        title=content_request.title,
        format=content_request.output_format,
        research=content_request.include_research,
    )

    try:
        from ..tools.generators.unified_content_creator import create_unified_content as create_content

        result = await create_content(
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

        logger.info("Unified content creation completed successfully")
        return {"status": "success", "data": response_data, "timestamp": datetime.now(UTC).isoformat()}

    except Exception as e:
        logger.error("Unified content creation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# Voice Mode Endpoints (if enabled)
@app.post(
    "/api/v1/voice/transcribe",
    response_model=dict[str, Any],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Voice Mode"],
    summary="Speech to Text",
    description="Convert audio input to text using OpenAI Whisper or Google Speech-to-Text.",
)
async def voice_transcribe(audio: UploadFile):
    """Convert speech to text."""
    if not config.is_feature_enabled("voice_mode"):
        raise HTTPException(status_code=404, detail="Voice mode is disabled")

    try:
        from .voice_interface import voice_interface

        text = await voice_interface.speech_to_text(audio)

        return {"status": "success", "transcribed_text": text, "timestamp": datetime.now(UTC).isoformat()}
    except Exception as e:
        logger.error("Speech transcription failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/voice/speak",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Voice Mode"],
    summary="Text to Speech",
    description="Convert text to speech audio using OpenAI TTS or Google Text-to-Speech.",
)
async def voice_speak(text: str = Form(...), voice: str = Form("alloy")):
    """Convert text to speech and return audio stream."""
    if not config.is_feature_enabled("voice_mode"):
        raise HTTPException(status_code=404, detail="Voice mode is disabled")

    try:
        from .voice_interface import create_audio_stream

        return await create_audio_stream(text, voice)
    except Exception as e:
        logger.error("Text-to-speech failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post(
    "/api/v1/voice/content",
    response_model=dict[str, Any],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Voice Mode"],
    summary="Voice Content Creation",
    description=(
        "Create content from voice input - transcribe audio, generate content, " "and optionally return audio response."
    ),
)
async def voice_content_creation(
    audio: UploadFile,
    content_type: str = Form("article"),
    return_audio: bool = Form(False),
    voice: str = Form("alloy"),
):
    """Process voice input for content creation."""
    if not config.is_feature_enabled("voice_mode"):
        raise HTTPException(status_code=404, detail="Voice mode is disabled")

    try:
        from .voice_interface import process_voice_content_request

        result = await process_voice_content_request(audio, content_type)

        if not return_audio:
            # Remove audio response to reduce payload size
            result.pop("audio_response", None)

        return {"status": "success", "data": result, "timestamp": datetime.now(UTC).isoformat()}
    except Exception as e:
        logger.error("Voice content creation failed", error=e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add custom schema extensions
    openapi_schema["info"]["x-logo"] = {"url": "https://github.com/adrshkr/mcp-server-openai/raw/main/docs/logo.png"}

    # Add server information
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://your-cloud-run-url", "description": "Production server"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
