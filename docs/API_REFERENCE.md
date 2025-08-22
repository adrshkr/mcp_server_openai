# 🔌 Unified Content Creator System - Complete API Reference

## 📋 Overview

This document provides a comprehensive reference for all API endpoints, tools, and data structures in the Unified Content Creator System.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REST API Server                         │
│                         Port 8000                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ HTML  │   │ DOC   │   │ PPT   │
│ Gen   │   │ Gen   │   │ Gen   │
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
        ┌───────▼───────┐
        │ Image & Icon  │
        │  Generators   │
        └───────────────┘
```

## 🔌 REST API Endpoints

### Base URL
```
http://localhost:8000
```

### Health and Status

#### GET /health
**Description**: System health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "2.0.0",
  "services": {
    "unified_content_creator": "healthy",
    "mcp_sequential_thinking": "healthy",
    "mcp_brave_search": "healthy",
    "mcp_memory": "healthy",
    "mcp_filesystem": "healthy",
    "mcp_research_integration": "healthy",
    "mcp_content_validation": "healthy",
    "mcp_advanced_orchestration": "healthy"
  }
}
```

#### GET /info
**Description**: System information and configuration

**Response**:
```json
{
  "system_name": "Unified Content Creator System",
  "version": "2.0.0",
  "environment": "production",
  "uptime": "2h 15m 30s",
  "memory_usage": "512MB",
  "cpu_usage": "15%",
  "active_connections": 25,
  "total_requests": 1250
}
```

#### GET /metrics
**Description**: Prometheus metrics endpoint

**Response**: Prometheus-formatted metrics

### Enhanced PPT Generator

#### POST /api/v1/ppt/generate
**Description**: Generate PowerPoint presentation

**Request Body**:
```json
{
  "title": "AI in Modern Business",
  "brief": "Comprehensive overview of AI applications in business",
  "notes": [
    "Machine learning applications",
    "Automation benefits",
    "Future trends"
  ],
  "content_style": "professional",
  "language": "en",
  "slide_count": 10,
  "include_images": true,
  "include_icons": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "file_path": "/output/ai_modern_business_20240101_120000.pptx",
  "slide_count": 10,
  "file_size": 2048576,
  "generation_time": 15.5,
  "metadata": {
    "title": "AI in Modern Business",
    "style": "professional",
    "language": "en",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Enhanced Document Generator

#### POST /api/v1/document/generate
**Description**: Generate documents in various formats

**Request Body**:
```json
{
  "title": "Technical Documentation",
  "content": "# Technical Documentation\n\nThis is the main content...",
  "output_format": "html",
  "template": "professional",
  "language": "en",
  "custom_css": null,
  "include_toc": true,
  "include_page_numbers": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Document generated successfully",
  "file_path": "/output/technical_documentation_20240101_120000.html",
  "file_size": 15360,
  "generation_time": 8.2,
  "metadata": {
    "title": "Technical Documentation",
    "format": "html",
    "template": "professional",
    "language": "en",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Enhanced Image Generator

#### POST /api/v1/image/generate
**Description**: Generate images using multiple providers

**Request Body**:
```json
{
  "query": "professional business meeting",
  "content_type": "content",
  "style": "professional",
  "count": 3,
  "format": "jpeg",
  "quality": "high",
  "size": "medium",
  "provider": "unsplash"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Images generated successfully",
  "images": [
    {
      "file_path": "/output/business_meeting_1_20240101_120000.jpg",
      "provider": "unsplash",
      "url": "https://unsplash.com/photos/abc123",
      "metadata": {
        "width": 1024,
        "height": 768,
        "format": "jpeg",
        "size": 512000
      }
    }
  ],
  "generation_time": 12.5,
  "total_count": 3
}
```

### Enhanced Icon Generator

#### POST /api/v1/icon/generate
**Description**: Generate icons using multiple providers

**Request Body**:
```json
{
  "query": "business",
  "style": "professional",
  "size": "medium",
  "format": "svg",
  "provider": "lucide"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Icons generated successfully",
  "icons": [
    {
      "file_path": "/output/business_icon_20240101_120000.svg",
      "provider": "lucide",
      "name": "briefcase",
      "metadata": {
        "width": 64,
        "height": 64,
        "format": "svg",
        "size": 2048
      }
    }
  ],
  "generation_time": 2.1,
  "total_count": 1
}
```

### Unified Content Creator

#### POST /api/v1/unified/create
**Description**: Create content using unified interface

**Request Body**:
```json
{
  "title": "Comprehensive Business Report",
  "brief": "Complete business analysis and strategy",
  "notes": [
    "Market analysis",
    "Competitive landscape",
    "Strategic recommendations",
    "Implementation plan"
  ],
  "output_format": "html",
  "content_style": "executive",
  "language": "en",
  "include_images": true,
  "include_icons": true,
  "research_depth": "comprehensive",
  "validate_content": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Unified content created successfully",
  "content_type": "html",
  "file_path": "/output/comprehensive_business_report_20240101_120000.html",
  "file_size": 25600,
  "generation_time": 45.2,
  "content_plan": {
    "sections": [
      {
        "title": "Executive Summary",
        "content": "Overview of business analysis...",
        "order": 1
      }
    ]
  },
  "research_results": {
    "sources": ["source1", "source2"],
    "key_findings": ["finding1", "finding2"]
  },
  "images": [
    {
      "file_path": "/output/chart_1_20240101_120000.png",
      "description": "Market growth chart"
    }
  ],
  "icons": [
    {
      "file_path": "/output/icon_1_20240101_120000.svg",
      "description": "Business icon"
    }
  ],
  "validation_results": {
    "content_quality_score": 0.85,
    "readability_score": 0.82,
    "seo_score": 0.78
  }
}
```

## 🧠 MCP Server Tools

### Sequential Thinking Server

#### Tool: create_content_plan
**Description**: Create AI-powered content planning and structure

**Parameters**:
```json
{
  "title": "string",
  "brief": "string",
  "target_audience": "string",
  "duration_minutes": "integer",
  "content_style": "string",
  "complexity_level": "string"
}
```

**Response**:
```json
{
  "success": true,
  "sections": [
    {
      "title": "string",
      "content": "string",
      "order": "integer",
      "estimated_duration": "integer",
      "key_points": ["string"]
    }
  ],
  "total_duration": "integer",
  "complexity_assessment": "string"
}
```

#### Tool: enhance_content_with_research
**Description**: Enhance content using research data

**Parameters**:
```json
{
  "content_plan_id": "string",
  "research_id": "string",
  "enhancement_focus": "string"
}
```

**Response**:
```json
{
  "success": true,
  "enhanced_sections": [
    {
      "original_section": "object",
      "enhanced_content": "string",
      "research_sources": ["string"],
      "improvements": ["string"]
    }
  ]
}
```

### Brave Search Server

#### Tool: search_web
**Description**: Perform web search for content research

**Parameters**:
```json
{
  "query": "string",
  "max_results": "integer",
  "search_type": "string",
  "language": "string",
  "region": "string"
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "relevance_score": "float",
      "source_type": "string"
    }
  ],
  "total_results": "integer",
  "search_time": "float"
}
```

#### Tool: analyze_content_relevance
**Description**: Analyze content relevance to search query

**Parameters**:
```json
{
  "content": "string",
  "search_query": "string",
  "analysis_depth": "string"
}
```

**Response**:
```json
{
  "success": true,
  "relevance_score": "float",
  "key_matches": ["string"],
  "suggested_improvements": ["string"],
  "confidence_level": "float"
}
```

### Memory Server

#### Tool: store_content
**Description**: Store content in memory for later retrieval

**Parameters**:
```json
{
  "content_id": "string",
  "content_type": "string",
  "content": "object",
  "metadata": "object",
  "expiration": "string"
}
```

**Response**:
```json
{
  "success": true,
  "stored_id": "string",
  "storage_time": "string",
  "size_bytes": "integer"
}
```

#### Tool: retrieve_content
**Description**: Retrieve stored content from memory

**Parameters**:
```json
{
  "content_id": "string",
  "include_metadata": "boolean"
}
```

**Response**:
```json
{
  "success": true,
  "content": "object",
  "metadata": "object",
  "retrieved_at": "string"
}
```

#### Tool: search_memory
**Description**: Search stored content in memory

**Parameters**:
```json
{
  "query": "string",
  "content_type": "string",
  "limit": "integer",
  "include_metadata": "boolean"
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "content_id": "string",
      "content": "object",
      "relevance_score": "float",
      "metadata": "object"
    }
  ],
  "total_results": "integer"
}
```

### Filesystem Server

#### Tool: read_file
**Description**: Read file contents safely

**Parameters**:
```json
{
  "file_path": "string",
  "encoding": "string",
  "max_size": "integer"
}
```

**Response**:
```json
{
  "success": true,
  "content": "string",
  "file_size": "integer",
  "last_modified": "string"
}
```

#### Tool: write_file
**Description**: Write content to file safely

**Parameters**:
```json
{
  "file_path": "string",
  "content": "string",
  "encoding": "string",
  "overwrite": "boolean"
}
```

**Response**:
```json
{
  "success": true,
  "file_path": "string",
  "bytes_written": "integer",
  "write_time": "string"
}
```

#### Tool: list_directory
**Description**: List directory contents safely

**Parameters**:
```json
{
  "directory_path": "string",
  "include_hidden": "boolean",
  "max_items": "integer"
}
```

**Response**:
```json
{
  "success": true,
  "items": [
    {
      "name": "string",
      "type": "string",
      "size": "integer",
      "modified": "string"
    }
  ],
  "total_items": "integer"
}
```

### Research Integration Server

#### Tool: conduct_research
**Description**: Conduct comprehensive research on a topic

**Parameters**:
```json
{
  "topic": "string",
  "research_depth": "string",
  "sources": ["string"],
  "max_results": "integer",
  "include_analysis": "boolean"
}
```

**Response**:
```json
{
  "success": true,
  "research_id": "string",
  "findings": [
    {
      "source": "string",
      "content": "string",
      "relevance_score": "float",
      "key_points": ["string"]
    }
  ],
  "summary": "string",
  "recommendations": ["string"],
  "research_time": "float"
}
```

#### Tool: analyze_research_quality
**Description**: Analyze quality and reliability of research

**Parameters**:
```json
{
  "research_id": "string",
  "quality_metrics": ["string"]
}
```

**Response**:
```json
{
  "success": true,
  "quality_score": "float",
  "reliability_assessment": "string",
  "bias_analysis": "string",
  "source_credibility": ["string"]
}
```

### Content Validation Server

#### Tool: validate_content
**Description**: Validate content quality and compliance

**Parameters**:
```json
{
  "content": "string",
  "content_type": "string",
  "validation_rules": ["string"],
  "quality_thresholds": "object"
}
```

**Response**:
```json
{
  "success": true,
  "validation_results": {
    "content_quality_score": "float",
    "readability_score": "float",
    "seo_score": "float",
    "accessibility_score": "float",
    "compliance_score": "float"
  },
  "issues": [
    {
      "type": "string",
      "severity": "string",
      "description": "string",
      "suggestion": "string"
    }
  ],
  "recommendations": ["string"]
}
```

#### Tool: optimize_content
**Description**: Optimize content based on validation results

**Parameters**:
```json
{
  "content": "string",
  "validation_results": "object",
  "optimization_focus": ["string"],
  "target_audience": "string"
}
```

**Response**:
```json
{
  "success": true,
  "optimized_content": "string",
  "improvements_made": ["string"],
  "new_scores": "object",
  "optimization_time": "float"
}
```

### Advanced Orchestration Server

#### Tool: create_workflow
**Description**: Create complex content creation workflows

**Parameters**:
```json
{
  "workflow_name": "string",
  "steps": [
    {
      "step_id": "string",
      "tool_name": "string",
      "parameters": "object",
      "dependencies": ["string"],
      "conditions": "object"
    }
  ],
  "parallel_execution": "boolean",
  "error_handling": "object"
}
```

**Response**:
```json
{
  "success": true,
  "workflow_id": "string",
  "estimated_duration": "float",
  "resource_requirements": "object",
  "validation_results": "object"
}
```

#### Tool: execute_workflow
**Description**: Execute a defined workflow

**Parameters**:
```json
{
  "workflow_id": "string",
  "input_data": "object",
  "execution_mode": "string",
  "monitoring": "boolean"
}
```

**Response**:
```json
{
  "success": true,
  "execution_id": "string",
  "status": "string",
  "current_step": "string",
  "progress": "float",
  "results": "object"
}
```

## 📊 Data Structures

### Common Request/Response Fields

#### Base Request
```json
{
  "request_id": "string",
  "timestamp": "string",
  "user_id": "string",
  "session_id": "string"
}
```

#### Base Response
```json
{
  "success": "boolean",
  "message": "string",
  "request_id": "string",
  "timestamp": "string",
  "execution_time": "float"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object",
    "suggestions": ["string"]
  },
  "request_id": "string",
  "timestamp": "string"
}
```

### Content Generation Models

#### PPTRequest
```json
{
  "title": "string",
  "brief": "string",
  "notes": ["string"],
  "content_style": "string",
  "language": "string",
  "slide_count": "integer",
  "include_images": "boolean",
  "include_icons": "boolean",
  "template": "string",
  "custom_styling": "object"
}
```

#### DocumentRequest
```json
{
  "title": "string",
  "content": "string",
  "output_format": "string",
  "template": "string",
  "language": "string",
  "custom_css": "string",
  "include_toc": "boolean",
  "include_page_numbers": "boolean",
  "metadata": "object"
}
```

#### ImageRequest
```json
{
  "query": "string",
  "content_type": "string",
  "style": "string",
  "count": "integer",
  "format": "string",
  "quality": "string",
  "size": "string",
  "provider": "string",
  "custom_parameters": "object"
}
```

#### IconRequest
```json
{
  "query": "string",
  "style": "string",
  "size": "string",
  "format": "string",
  "provider": "string",
  "color_scheme": "string",
  "custom_parameters": "object"
}
```

#### UnifiedContentRequest
```json
{
  "title": "string",
  "brief": "string",
  "notes": ["string"],
  "output_format": "string",
  "content_style": "string",
  "language": "string",
  "include_images": "boolean",
  "include_icons": "boolean",
  "research_depth": "string",
  "validate_content": "boolean",
  "custom_parameters": "object"
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Optional
PRESENTON_API_KEY=your-presenton-api-key
UNSPLASH_API_KEY=your-unsplash-api-key
STABLE_DIFFUSION_API_KEY=your-stable-diffusion-api-key
PIXABAY_API_KEY=your-pixabay-api-key
BRAVE_SEARCH_API_KEY=your-brave-search-api-key

# System Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
OUTPUT_DIR=/app/output
MAX_FILE_SIZE=10485760
REQUEST_TIMEOUT=300
```

### Configuration File

```yaml
# config/unified_system_complete.yaml
system:
  name: "Unified Content Creator System"
  version: "2.0.0"
  environment: "production"
  debug: false
  log_level: "INFO"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 300
  rate_limit: 1000
  cors_origins: ["*"]

content_generation:
  enhanced_ppt_generator:
    enabled: true
    default_model: "gpt-4o"
    max_slides: 100
    templates: ["professional", "creative", "educational", "marketing"]
    
  enhanced_document_generator:
    enabled: true
    default_format: "html"
    templates: ["professional", "modern", "minimal", "creative"]
    max_file_size: 10485760
    
  enhanced_image_generator:
    enabled: true
    providers: ["unsplash", "stable_diffusion", "pixabay"]
    default_provider: "unsplash"
    max_image_count: 10
    
  enhanced_icon_generator:
    enabled: true
    providers: ["lucide", "iconify"]
    default_provider: "lucide"
    max_icon_count: 20
```

## 🚀 Usage Examples

### Python Client Example

```python
import httpx
import json

class UnifiedContentCreatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_presentation(self, title, brief, notes):
        """Create a PowerPoint presentation"""
        request_data = {
            "title": title,
            "brief": brief,
            "notes": notes,
            "content_style": "professional",
            "language": "en",
            "slide_count": len(notes),
            "include_images": True,
            "include_icons": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/ppt/generate",
            json=request_data
        )
        
        return response.json()
    
    async def create_document(self, title, content, output_format="html"):
        """Create a document in specified format"""
        request_data = {
            "title": title,
            "content": content,
            "output_format": output_format,
            "template": "professional",
            "language": "en"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/document/generate",
            json=request_data
        )
        
        return response.json()
    
    async def create_unified_content(self, title, brief, notes, output_format="html"):
        """Create content using unified interface"""
        request_data = {
            "title": title,
            "brief": brief,
            "notes": notes,
            "output_format": output_format,
            "content_style": "professional",
            "language": "en",
            "include_images": True,
            "include_icons": True,
            "research_depth": "comprehensive",
            "validate_content": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/unified/create",
            json=request_data
        )
        
        return response.json()

# Usage example
async def main():
    client = UnifiedContentCreatorClient()
    
    # Create presentation
    ppt_result = await client.create_presentation(
        title="AI in Business",
        brief="Overview of AI applications in business",
        notes=["Introduction", "Applications", "Benefits", "Future Trends"]
    )
    
    print(f"Presentation created: {ppt_result['file_path']}")
    
    # Create unified content
    unified_result = await client.create_unified_content(
        title="Comprehensive Business Report",
        brief="Complete business analysis",
        notes=["Market Analysis", "Strategy", "Implementation"],
        output_format="pdf"
    )
    
    print(f"Unified content created: {unified_result['file_path']}")

# Run the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### cURL Examples

#### Create PowerPoint Presentation
```bash
curl -X POST http://localhost:8000/api/v1/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI in Modern Business",
    "brief": "Comprehensive overview of AI applications in business",
    "notes": [
      "Machine learning applications",
      "Automation benefits",
      "Future trends"
    ],
    "content_style": "professional",
    "language": "en",
    "slide_count": 10,
    "include_images": true,
    "include_icons": true
  }'
```

#### Generate HTML Document
```bash
curl -X POST http://localhost:8000/api/v1/document/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Technical Documentation",
    "content": "# Technical Documentation\n\nThis is the main content...",
    "output_format": "html",
    "template": "professional",
    "language": "en",
    "include_toc": true,
    "include_page_numbers": true
  }'
```

#### Generate Images
```bash
curl -X POST http://localhost:8000/api/v1/image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "professional business meeting",
    "content_type": "content",
    "style": "professional",
    "count": 3,
    "format": "jpeg",
    "quality": "high",
    "size": "medium",
    "provider": "unsplash"
  }'
```

#### Create Unified Content
```bash
curl -X POST http://localhost:8000/api/v1/unified/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Comprehensive Business Report",
    "brief": "Complete business analysis and strategy",
    "notes": [
      "Market analysis",
      "Competitive landscape",
      "Strategic recommendations",
      "Implementation plan"
    ],
    "output_format": "html",
    "content_style": "executive",
    "language": "en",
    "include_images": true,
    "include_icons": true,
    "research_depth": "comprehensive",
    "validate_content": true
  }'
```

## 📚 Additional Resources

- **Configuration Guide**: [config/unified_system_complete.yaml](config/unified_system_complete.yaml)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Testing Guide**: [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)
- **Architecture Documentation**: [docs/TOOL_ARCHITECTURE_WORKFLOW.md](docs/TOOL_ARCHITECTURE_WORKFLOW.md)

---

**Happy API Integration! 🔌**
