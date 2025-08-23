"""
Enhanced FastAPI server with comprehensive API documentation.

This module provides a FastAPI-based server with OpenAPI documentation,
request validation, and improved error handling.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

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
from .request_handlers import (
    DocumentRequestHandler,
    IconRequestHandler,
    ImageRequestHandler,
    PPTRequestHandler,
    UnifiedContentRequestHandler,
)

# Initialize core systems
config = get_config()
logger = get_logger("fastapi_server")
error_handler = get_error_handler()

# Initialize request handlers
ppt_handler = PPTRequestHandler()
document_handler = DocumentRequestHandler()
image_handler = ImageRequestHandler()
icon_handler = IconRequestHandler()
unified_handler = UnifiedContentRequestHandler()


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


# Health and monitoring endpoints
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Basic health check",
    description="Simple health check endpoint that returns server status."
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
    description="Liveness probe for container orchestration. Used to determine if container should be restarted."
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
    description="Readiness probe for container orchestration. Used to determine if container can accept traffic."
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
    response_model=Dict[str, Any],
    tags=["Health"],
    summary="Detailed status",
    description="Comprehensive system status with detailed diagnostics."
)
async def detailed_status():
    """Detailed status endpoint."""
    from ..health import health_checker
    
    return await health_checker.detailed_status()


@app.get(
    "/info",
    response_model=Dict[str, Any],
    tags=["Information"],
    summary="Service information",
    description="Service metadata, available endpoints, and feature flags."
)
async def service_info():
    """Service information endpoint."""
    return {
        "service": "MCP Server OpenAI",
        "version": "0.2.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "ppt_generation": "/api/v1/ppt/generate",
            "document_generation": "/api/v1/document/generate",
            "image_generation": "/api/v1/image/generate",
            "icon_generation": "/api/v1/icon/generate",
            "unified_content": "/api/v1/unified/create",
        },
        "features": {
            "ppt_generation": config.features.enable_ppt_generation,
            "document_generation": config.features.enable_document_generation,
            "image_generation": config.features.enable_image_generation,
            "icon_generation": config.features.enable_icon_generation,
            "research_integration": config.features.enable_research,
            "caching": config.features.enable_caching,
            "monitoring": config.features.enable_monitoring,
        },
        "documentation": {
            "openapi": "/openapi.json",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        }
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
    """
)
async def generate_ppt(request: Request, ppt_request: PPTRequest):
    """Generate PowerPoint presentation."""
    logger.info("PPT generation request received", 
               notes_count=len(ppt_request.notes),
               template=ppt_request.template_preference)
    
    return await ppt_handler.handle_generation(request)


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
    """
)
async def generate_document(request: Request, doc_request: DocumentRequest):
    """Generate document in specified format."""
    logger.info("Document generation request received",
               format=doc_request.output_format,
               template=doc_request.template)
    
    return await document_handler.handle_generation(request)


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
    """
)
async def generate_image(request: Request, image_request: ImageRequest):
    """Generate or find relevant images."""
    logger.info("Image generation request received",
               query=image_request.query,
               style=image_request.style,
               count=image_request.count)
    
    return await image_handler.handle_generation(request)


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
    """
)
async def generate_icon(request: Request, icon_request: IconRequest):
    """Generate matching icons."""
    logger.info("Icon generation request received",
               query=icon_request.query,
               style=icon_request.style,
               provider=icon_request.provider)
    
    return await icon_handler.handle_generation(request)


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
    """
)
async def create_unified_content(request: Request, content_request: UnifiedContentRequest):
    """Create unified content with comprehensive features."""
    logger.info("Unified content creation request received",
               title=content_request.title,
               format=content_request.output_format,
               research=content_request.include_research)
    
    return await unified_handler.handle_creation(request)


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
    openapi_schema["info"]["x-logo"] = {
        "url": "https://github.com/adrshkr/mcp-server-openai/raw/main/docs/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://your-cloud-run-url",
            "description": "Production server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
