# 🚀 MCP Server OpenAI - AI Content Creation Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com/adrshkr/mcp-server-openai)
[![GCP Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run-4285f4.svg)](https://cloud.google.com/run)

> **Create professional presentations, documents, and web content with AI-powered tools. Production-ready with enterprise security and monitoring.**

## 🎯 What This Platform Does

**MCP Server OpenAI** is an AI-powered content creation platform that helps you generate:

- 📊 **PowerPoint Presentations** - Professional slides with AI-generated content, images, and icons
- 📄 **Documents** - Word docs, PDFs, HTML pages with smart formatting and research integration
- 🖼️ **Images & Icons** - AI-generated visuals that perfectly match your content
- 🔍 **Research-Enhanced Content** - Automatically researched, fact-checked, and optimized content

**Perfect for:** Business professionals, educators, content creators, marketers, and anyone who needs to create professional content quickly and efficiently.

## ⚡ Quick Start (5 Minutes)

### **Prerequisites**
- Python 3.11+ installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### **1. Install & Setup**
```bash
# Clone and enter the project
git clone https://github.com/adrshkr/mcp-server-openai.git
cd mcp-server-openai

# Install dependencies (fast with uv)
pip install uv
uv sync

# Set up your API key
echo "OPENAI_API_KEY=your-actual-key-here" > .env
```

### **2. Start the Server**
```bash
# Quick start (recommended)
python scripts/utilities/startup.py

# Or manually
python -m mcp_server_openai --http --port 8000
```

### **3. Test It Works**
```bash
# Check server health
curl http://localhost:8000/health

# Create your first presentation
curl -X POST http://localhost:8000/api/v1/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "notes": ["Introduction to AI", "Benefits of automation", "Future outlook"],
    "brief": "AI presentation for business meeting"
  }'
```

**🎉 That's it!** Your AI content creation server is now running at `http://localhost:8000`

## 🛠️ What You Can Create

### **📊 Professional Presentations**
```bash
POST /api/v1/ppt/generate
{
  "notes": ["Market analysis", "Growth projections", "Recommendations"],
  "brief": "Q4 business review presentation",
  "template_preference": "professional",
  "include_images": true
}
```

### **📄 Smart Documents**
```bash
POST /api/v1/document/generate
{
  "title": "Project Report",
  "content": "# Executive Summary\n\nProject overview...",
  "output_format": "pdf",
  "template": "corporate"
}
```

### **🖼️ Contextual Images**
```bash
POST /api/v1/image/generate
{
  "query": "modern office workspace",
  "style": "professional",
  "format": "jpeg"
}
```

### **🎨 Matching Icons**
```bash
POST /api/v1/icon/generate
{
  "query": "technology innovation",
  "style": "outline",
  "size": "medium"
}
```

## ✨ Key Features

- **🎯 Unified Content Creation**: Single API for presentations, documents, images, and icons
- **🧠 AI-Powered Planning**: Intelligent content structuring and research integration
- **🎨 Professional Templates**: Multiple styles for business, academic, and creative content
- **🔍 Auto-Research**: Automatically enhance content with web research and fact-checking
- **🖼️ Visual Enhancement**: AI-generated images and icons that match your content perfectly
- **⚡ Fast & Reliable**: Production-ready with health monitoring and error handling
- **🔒 Enterprise Security**: Secure API key management and hardened deployment
- **🚀 Easy Deployment**: One-command deployment to Google Cloud Run or Docker

## 📁 Project Structure

```
mcp_server_openai/
├── 📄 Core Files
│   ├── README.md              # Main documentation
│   ├── LICENSE               # MIT license
│   ├── Makefile             # Development commands
│   ├── pyproject.toml       # Python project configuration
│   ├── requirements.txt     # Production dependencies
│   └── uv.lock             # Lock file for reproducible builds
│
├── 🏗️ Source Code
│   └── src/mcp_server_openai/
│       ├── __init__.py      # Package initialization
│       ├── __main__.py      # CLI entry point
│       ├── main.py          # MCP server entry point
│       ├── server.py        # Core MCP server
│       ├── health.py        # Health check logic
│       ├── security.py      # Security validation
│       │
│       ├── 🌐 API Layer
│       │   ├── http_server.py    # HTTP server implementation
│       │   └── streaming_http.py # Streaming endpoints
│       │
│       ├── 🔧 Tools (MCP Tools)
│       │   ├── generators/       # Content generation tools
│       │   │   ├── content_creator.py
│       │   │   ├── enhanced_ppt_generator.py
│       │   │   ├── enhanced_document_generator.py
│       │   │   └── unified_content_creator.py
│       │   │
│       │   ├── mcp_integrations/ # MCP server integrations
│       │   │   ├── mcp_sequential_thinking.py
│       │   │   ├── mcp_content_validation.py
│       │   │   └── mcp_research_integration.py
│       │   │
│       │   └── utilities/        # General utility tools
│       │       ├── math_tools.py
│       │       └── web_tools.py
│       │
│       ├── 📝 Prompts
│       │   ├── templates/    # Jinja2 templates
│       │   ├── content_create.py
│       │   └── manager.py
│       │
│       ├── 📊 Monitoring
│       │   ├── cost_limiter.py
│       │   ├── usage_tracker.py
│       │   └── monitoring_config.py
│       │
│       └── 🔐 Resources
│           └── health.py     # Health check resources
│
├── ⚙️ Configuration
│   └── config/
│       ├── enhanced_*.yaml      # Tool configurations
│       ├── params-*.json        # Parameter files
│       ├── mcp-servers-config.json
│       ├── mypy.ini            # Type checking config
│       └── pytest.ini          # Test configuration
│
├── 🚀 Deployment
│   ├── docker/                 # Container images
│   │   ├── Dockerfile          # Main production image
│   │   ├── Dockerfile.enhanced # Enhanced features
│   │   └── Dockerfile.unified  # Unified system
│   │
│   ├── cloud-run/             # GCP Cloud Run configs
│   │   ├── cloud-run-service.yaml
│   │   └── config.yaml
│   │
│   ├── docker-compose.yml      # Local development
│   ├── docker-compose.complete.yml
│   │
│   └── scripts/               # Deployment automation
│       ├── deploy-optimized.sh
│       ├── deploy-to-cloud-run.sh
│       └── deploy-unified-system.sh
│
├── 📜 Scripts
│   ├── demos/                 # Demo and example scripts
│   │   ├── demo_enhanced_content.py
│   │   └── demo_unified_content.py
│   │
│   ├── testing/              # Test scripts
│   │   ├── test-deployment.py
│   │   ├── test_complete_system.py
│   │   └── test_unified_system.py
│   │
│   ├── utilities/            # System utilities
│   │   ├── startup.py        # Optimized startup
│   │   ├── preflight.py      # Pre-deployment checks
│   │   └── verify_endpoints.py
│   │
│   └── development/          # Development tools
│       ├── call_tool.py
│       └── register_mcp_configs.sh
│
├── 🧪 Tests
│   └── tests/
│       ├── test_*.py           # Unit and integration tests
│       ├── conftest.py         # Test configuration
│       └── test_sanity.py      # Basic functionality tests
│
├── 📚 Documentation
│   └── docs/
│       ├── API_REFERENCE.md    # API documentation
│       ├── DEPLOYMENT_GUIDE.md # Deployment instructions
│       ├── README-SECURITY.md  # Security guidelines
│       └── TESTING_GUIDE.md    # Testing strategies
│
├── 🎨 Templates
│   └── templates/
│       ├── html/              # HTML templates
│       │   ├── professional.html
│       │   └── corporate.html
│       └── pandoc/            # Pandoc templates
│
├── 🔧 Tools
│   └── tools/
│       ├── ccstatusline/      # Status line tool
│       ├── notify.ps1         # Windows notification
│       └── statusline-manager.sh
│
├── 📊 Data & Output
│   ├── data/                  # Runtime data
│   │   ├── files/
│   │   └── memory.db
│   │
│   ├── output/               # Generated content
│   │   ├── documents/
│   │   └── presentations/
│   │
│   ├── logs/                 # Log files
│   │   └── mcp_server.log
│   │
│   ├── examples/             # Example files
│   └── build/                # Build artifacts
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Content Creator                  │
│                     (Main Orchestrator)                    │
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

### 🔧 MCP Server Ecosystem

- **Sequential Thinking Server** (Port 3001): AI-powered content planning
- **Brave Search Server** (Port 3002): Web research and content enhancement
- **Memory Server** (Port 3003): Content storage and context management
- **Filesystem Server** (Port 3004): File operations and management
- **Research Integration** (Port 3005): Automated research workflows
- **Content Validation** (Port 3006): Quality assessment and optimization
- **Advanced Orchestration** (Port 3007): Complex workflow management

## 🏥 Health Monitoring & Observability

### Health Check Endpoints

The server provides comprehensive health monitoring for production deployment:

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/health` | Basic health check | Legacy compatibility |
| `/health/live` | **Liveness Probe** | Container restart decisions (GCP Cloud Run) |
| `/health/ready` | **Readiness Probe** | Traffic routing decisions |
| `/health/startup` | **Startup Probe** | Container initialization validation |
| `/status` | **Detailed Status** | Comprehensive system diagnostics |
| `/info` | **Service Info** | API discovery and metadata |

### Health Check Response Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "healthy|unhealthy|not_ready",
  "uptime": 3600.5,
  "checks": {
    "config": {"status": "healthy", "valid": true},
    "database": {"status": "healthy", "type": "postgresql"},
    "resources": {"status": "healthy", "memory": {"percent": 45.2}},
    "dependencies": {"status": "healthy", "failed_dependencies": []},
    "api_keys": {"status": "healthy", "valid_keys": 3}
  }
}
```

### Performance Monitoring

- **Response Times**: Target P95 < 500ms, P99 < 1000ms
- **Resource Usage**: Memory < 90%, CPU < 90%
- **Error Rates**: Warning at 1%, Critical at 5%
- **Availability**: 99.9% uptime target

## 🔒 Security & Production Deployment

### Security Features

- **🔐 Zero Secret Exposure**: All API keys managed via GCP Secret Manager
- **👤 Non-root Execution**: Containers run as unprivileged user (UID 1000)
- **🛡️ Minimal Attack Surface**: Multi-stage Docker builds with runtime-only dependencies
- **🔒 Secure Defaults**: HTTPS enforcement, security headers, input validation
- **📋 Compliance**: Production-ready security configuration validation

### GCP Secret Manager Integration

```bash
# Create secrets in GCP Secret Manager
echo "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo "your-anthropic-key" | gcloud secrets create anthropic-api-key --data-file=-

# Secrets are automatically injected as environment variables in Cloud Run
```

### Security Validation

The security module validates all configuration at startup:

```python
from mcp_server_openai.security import validate_configuration

# Validates API keys, checks for compromised values, ensures secure defaults
validate_configuration()
```

⚠️ **CRITICAL**: If you're setting up this server, please review `README-SECURITY.md` for complete security setup instructions and emergency procedures.

## 🌐 Deploy to Production

### **Option 1: Google Cloud Run (Recommended)**
```bash
# One-command deployment with enterprise security
./deployment/scripts/deploy-optimized.sh

# Your server will be live at: https://your-service-url
# Includes: SSL, health checks, auto-scaling, monitoring
```

### **Option 2: Docker**
```bash
# Build and run with Docker
docker build -t mcp-server .
docker run -p 8000:8000 --env-file .env mcp-server

# Or use docker-compose for full stack
docker-compose -f docker-compose.complete.yml up
```

### **Option 3: Local Production**
```bash
# Run with production settings
uvicorn mcp_server_openai.api.http_server:app \
  --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Configuration

### **Required Environment Variables**
```bash
OPENAI_API_KEY=your-openai-key        # Required for AI features
```

### **Optional API Keys** (for enhanced features)
```bash
ANTHROPIC_API_KEY=your-anthropic-key  # Claude AI integration
GOOGLE_API_KEY=your-google-key        # Google AI features
UNSPLASH_ACCESS_KEY=your-unsplash-key # Stock photos
PIXABAY_API_KEY=your-pixabay-key      # More stock photos
BRAVE_SEARCH_API_KEY=your-brave-key   # Web research
```

### **Server Configuration**
```bash
# Server settings
HOST=0.0.0.0                         # Server host
PORT=8000                            # Server port
WORKERS=4                            # Number of workers

# Feature flags
ENABLE_MONITORING=true               # Health monitoring
ENABLE_CACHING=false                 # Response caching
DEBUG=false                          # Debug mode
```

## 📊 Health & Monitoring

Your server includes built-in monitoring and health checks:

### **Health Endpoints**
- **Basic Health**: `GET /health` - Simple server status
- **Liveness Probe**: `GET /health/live` - Container restart decisions
- **Readiness Probe**: `GET /health/ready` - Traffic routing decisions
- **Detailed Status**: `GET /status` - Full system diagnostics
- **Service Info**: `GET /info` - Available endpoints and features

### **Example Health Response**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "healthy",
  "uptime": 3600.5,
  "checks": {
    "config": {"status": "healthy", "valid": true},
    "resources": {"status": "healthy", "memory": {"percent": 45.2}},
    "api_keys": {"status": "healthy", "valid_keys": 3}
  }
}
```

## 🚨 Troubleshooting

### **Server Won't Start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
uv sync

# Check API key
echo $OPENAI_API_KEY

# Check logs
tail -f logs/mcp_server.log
```

### **API Errors**
```bash
# Check server health
curl http://localhost:8000/status

# Test specific endpoint
curl -X POST http://localhost:8000/api/v1/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{"notes": ["test"], "brief": "test"}'
```

### **Performance Issues**
- **Slow responses**: Check API key limits and server resources
- **Memory issues**: Reduce workers: `--workers 1`
- **Timeout errors**: Increase timeout settings in configuration

### **Common Error Solutions**
| Error | Solution |
|-------|----------|
| `ImportError: No module named 'mcp_server_openai'` | Run `uv sync` or `pip install -e .` |
| `401 Unauthorized` | Check your `OPENAI_API_KEY` is valid |
| `Health check failed` | Verify all required environment variables are set |
| `Port already in use` | Change port: `--port 8001` or kill existing process |

## 🎨 Available Tools

| Tool | What It Does | Best For | API Endpoint |
|------|-------------|----------|--------------|
| **PPT Generator** | Creates PowerPoint presentations with AI content | Business meetings, education | `POST /api/v1/ppt/generate` |
| **Document Generator** | Creates Word/PDF/HTML documents | Reports, manuals, web pages | `POST /api/v1/document/generate` |
| **Image Generator** | Finds/creates relevant images | Visual content, presentations | `POST /api/v1/image/generate` |
| **Icon Generator** | Creates matching icons | UI elements, infographics | `POST /api/v1/icon/generate` |
| **Content Planner** | AI-powered content structuring | Complex projects, research | `POST /api/v1/mcp/sequential-thinking/think` |
| **Web Research** | Automated web research | Fact-checking, content enhancement | `POST /api/v1/mcp/brave-search/search` |
| **Content Validation** | Quality assessment and optimization | Content review, SEO | `POST /api/v1/mcp/validation/validate` |

## 📚 API Reference

### **Core Content Creation**

#### **Create Presentation**
```bash
POST /api/v1/ppt/generate
{
  "notes": ["Slide 1 content", "Slide 2 content"],
  "brief": "Presentation description",
  "template_preference": "professional|creative|modern",
  "include_images": true,
  "include_icons": true
}
```

#### **Generate Document**
```bash
POST /api/v1/document/generate
{
  "title": "Document Title",
  "content": "# Heading\n\nContent here...",
  "output_format": "pdf|docx|html|markdown",
  "template": "professional|academic|creative"
}
```

#### **Create Images**
```bash
POST /api/v1/image/generate
{
  "query": "modern office workspace",
  "style": "professional|creative|minimalist",
  "format": "jpeg|png|webp",
  "count": 1
}
```

### **Response Format**
All endpoints return consistent JSON responses:
```json
{
  "status": "success|error",
  "data": {
    "file_path": "/output/generated_file.pptx",
    "file_size": "2.1MB",
    "generation_time": "12.3s"
  },
  "message": "Content generated successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🛠️ Tool Documentation

### Enhanced PPT Generator

Creates professional PowerPoint presentations with AI enhancement.

**Features:**
- Multiple template styles (Professional, Creative, Modern, Classic, Minimalist)
- AI-powered content enhancement
- Automatic image and icon integration
- Presenton API integration for high-quality output

**Usage:**
```python
from mcp_server_openai.tools.enhanced_ppt_generator import create_enhanced_presentation

result = await create_enhanced_presentation(
    notes=["Slide 1 content", "Slide 2 content"],
    brief="Presentation description",
    template_preference="professional",
    include_images=True
)
```

### Enhanced Document Generator

Multi-format document generation with professional templates.

**Supported Formats:**
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format
- **HTML**: Web-ready HTML with responsive design
- **Markdown**: Simple, portable format
- **LaTeX**: Academic-quality documents
- **RTF**: Rich Text Format

**Features:**
- Multiple template styles (Professional, Academic, Creative, Minimalist, Corporate)
- Tailwind CSS integration for HTML
- Multiple backend engines (Pandoc, WeasyPrint, ReportLab)
- Automatic fallback mechanisms

**Usage:**
```python
from mcp_server_openai.tools.enhanced_document_generator import generate_document

result = await generate_document(
    title="My Document",
    content="# Title\n\nContent here...",
    output_format="html",
    template="professional"
)
```

### Enhanced Image Generator

Multi-provider image generation for content enhancement.

**Providers:**
- **Unsplash**: High-quality stock photos
- **Stable Diffusion**: AI-generated custom images
- **Pixabay**: Additional stock photo library

**Features:**
- Content-aware image selection
- Multiple formats (JPEG, PNG, WebP, SVG)
- Quality and size presets
- Style matching

**Usage:**
```python
from mcp_server_openai.tools.enhanced_image_generator import generate_image

result = await generate_image(
    query="modern technology",
    content_type="presentation",
    style="professional",
    count=1,
    format="jpeg"
)
```

### Enhanced Icon Generator

Multi-provider icon generation for visual enhancement.

**Providers:**
- **Iconify**: Extensive icon library
- **Lucide**: Modern, consistent icons
- **Custom AI**: AI-generated custom icons

**Features:**
- Context-aware icon selection
- Multiple formats (SVG, PNG, ICO, WebP)
- Size presets
- Style consistency

**Usage:**
```python
from mcp_server_openai.tools.enhanced_icon_generator import generate_icon

result = await generate_icon(
    query="technology",
    style="outline",
    size="medium",
    provider="lucide"
)
```

## 🔍 MCP Server Details

### Sequential Thinking Server

AI-powered content planning and structuring with a 5-step thinking process:

1. **Content Analysis**: Understanding requirements and context
2. **Structure Planning**: Creating logical content organization
3. **Content Structuring**: Detailed section planning
4. **Validation**: Quality and coherence checks
5. **Optimization**: Performance and effectiveness improvements

### Brave Search Server

Web search integration for content enhancement:

- **Web Search**: General web content discovery
- **News Search**: Current events and trends
- **Image Search**: Visual content discovery
- **Result Filtering**: Relevance and credibility assessment

### Memory Server

Content storage and context management:

- **Content Storage**: Persistent content storage
- **Context Retrieval**: Intelligent content retrieval
- **Metadata Indexing**: Searchable content organization
- **Cleanup Automation**: Automatic content lifecycle management

### Filesystem Server

Safe file operations and management:

- **File Operations**: Read, write, delete operations
- **Directory Management**: Folder creation and organization
- **Metadata Tracking**: File information and history
- **Safety Checks**: Path validation and security

### Research Integration Server

Automated research workflows:

- **Content-Type Patterns**: Specialized research for different content types
- **Source Analysis**: Credibility and relevance assessment
- **Insight Extraction**: Key information identification
- **Content Enhancement**: Research-based content improvement

### Content Validation Server

Quality assessment and optimization:

- **Readability**: Text complexity and accessibility
- **SEO**: Search engine optimization
- **Accessibility**: WCAG compliance
- **Grammar**: Language quality
- **Plagiarism**: Originality checking

### Advanced Orchestration Server

Complex workflow management:

- **Workflow Types**: Action, decision, parallel, loop, condition
- **Dependency Management**: Step dependencies and execution order
- **Conditional Logic**: Dynamic workflow paths
- **Progress Tracking**: Real-time execution monitoring
- **Execution History**: Comprehensive workflow logs

## 🧪 Testing

### Test Strategy & CI Optimization

The project uses a **fast/comprehensive test separation strategy** optimized for development speed and CI efficiency:

#### Fast Tests (Development & CI)
```bash
# Fast test suite (26s) - optimized for development
make test-fast
# OR
pytest -q --maxfail=1 --durations=10 -m "not slow and not integration and not e2e and not network"
```

**Excludes**: slow, integration, e2e, network tests  
**Purpose**: Quick validation during development and CI checks  
**Coverage**: Unit tests, fast integration tests, basic functionality  

#### Comprehensive Tests (Full Validation)
```bash
# Full test suite - comprehensive validation
make test-all
# OR
pytest -q --durations=10
```

**Includes**: All tests including slow/integration/e2e/network  
**Purpose**: Complete validation before releases  
**Coverage**: Full system testing, external dependencies, performance tests  

#### CI Integration
```bash
# Fast CI check (sub-30s total)
make check          # preflight + fast tests + mypy (core files)

# Full CI validation (comprehensive)  
make check-all      # preflight + all tests + mypy (full)
```

#### Test Markers
- `slow`: Long-running tests (>5s)
- `integration`: External service dependencies  
- `e2e`: End-to-end workflow tests
- `network`: Real network/API calls

### Test Configuration

**pytest.ini:**
```ini
[pytest]
addopts = -ra
testpaths = tests
asyncio_mode = auto
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests that require external services
    e2e: marks end-to-end tests
    network: marks tests that perform real network calls
```

### Running Tests

```bash
# Development workflow
make test           # Fast tests only (alias for test-fast)

# Complete validation  
make test-all       # All tests including slow/integration

# With coverage
pytest --cov=src --cov-report=html

# Specific markers
pytest -m "not slow"          # Exclude slow tests
pytest -m "integration"       # Run only integration tests
pytest -k "test_health"       # Run specific test patterns
```

### Test Coverage

The system includes comprehensive tests for:
- ✅ Unit tests for all components (fast)
- ✅ Integration tests for workflows (comprehensive)  
- ✅ Performance tests (slow marker)
- ✅ Error handling tests (fast)
- ✅ API endpoint tests (fast + e2e)

### Test Run Examples

#### Test Run 1: Enhanced PPT Generator
```bash
$ python scripts/test_complete_system.py --category=ppt

🧪 Testing Enhanced PPT Generator...
✅ Basic PPT generation: PASSED
✅ Custom style generation: PASSED
✅ Error handling: PASSED
✅ Image integration: PASSED
✅ Icon integration: PASSED

📊 Test Results Summary:
- Total Tests: 5
- Passed: 5
- Failed: 0
- Success Rate: 100%
- Execution Time: 12.3s

🎯 Generated Files:
- /output/test_presentation_20240101_120000.pptx (2.1MB)
- /output/creative_presentation_20240101_120000.pptx (1.8MB)
```

#### Test Run 2: Unified Content Creator (End-to-End)
```bash
$ python scripts/test_complete_system.py --category=unified

🧪 Testing Unified Content Creator...
✅ Content planning workflow: PASSED
✅ Research integration: PASSED
✅ Multi-format generation: PASSED
✅ Image and icon generation: PASSED
✅ Content validation: PASSED
✅ Complete workflow: PASSED

📊 Test Results Summary:
- Total Tests: 6
- Passed: 6
- Failed: 0
- Success Rate: 100%
- Execution Time: 45.7s

🎯 Generated Files:
- /output/business_report_20240101_120000.html (25.6KB)
- /output/business_report_20240101_120000.pdf (156.2KB)
- /output/business_report_20240101_120000.pptx (2.4MB)
- /output/chart_1_20240101_120000.png (512KB)
- /output/business_icon_20240101_120000.svg (2.1KB)

🔍 Content Quality Scores:
- Content Quality: 85%
- Readability: 82%
- SEO Score: 78%
- Accessibility: 89%

## 🚀 Deployment

### Local Docker Deployment

```bash
# Start all services
docker-compose -f docker-compose.complete.yml up -d

# View service status
docker-compose -f docker-compose.complete.yml ps

# View logs
docker-compose -f docker-compose.complete.yml logs -f
```

### Google Cloud Run Deployment

```bash
# Run deployment script
chmod +x scripts/deploy-complete-system.sh
./scripts/deploy-complete-system.sh
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/ -n unified-content

# Check deployment status
kubectl get pods -n unified-content
```

## 📊 Monitoring

### Health Checks

- **Main System**: `GET /health`
- **MCP Servers**: `GET /mcp/{server}/health`
- **Readiness**: `GET /ready`

### Metrics

- **Prometheus**: `GET /metrics`
- **Grafana Dashboards**: Available at `http://localhost:3000`

### Logging

- **Structured Logging**: JSON format with correlation IDs
- **Log Rotation**: Daily rotation with 30-day retention
- **Log Levels**: DEBUG, INFO, WARNING, ERROR

## 🔧 Configuration

### Environment Variables

**Required:**
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_API_KEY`: Google API key

**Optional:**
- `PRESENTON_API_KEY`: Presenton API key
- `UNSPLASH_API_KEY`: Unsplash API key
- `STABLE_DIFFUSION_API_KEY`: Stable Diffusion API key
- `PIXABAY_API_KEY`: Pixabay API key
- `BRAVE_SEARCH_API_KEY`: Brave Search API key

### Configuration Files

- **Main Config**: `config/unified_system_complete.yaml`
- **Tool Configs**: `config/enhanced_*.yaml`
- **Docker Config**: `docker-compose.complete.yml`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
black src/
isort src/
flake8 src/

# Run type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For GPT models and API
- **Anthropic**: For Claude models and API
- **Google**: For Gemini models and API
- **Presenton**: For PowerPoint generation API
- **Unsplash**: For stock photo API
- **Iconify**: For icon library API

## 📚 Learn More

- **[Complete Documentation](docs/)** - Full guides and advanced features
- **[Security Guide](docs/README-SECURITY.md)** - Production security setup
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Advanced deployment options
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

## 🤝 Support & Community

- **🐛 Issues**: [GitHub Issues](https://github.com/adrshkr/mcp-server-openai/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/adrshkr/mcp-server-openai/discussions)
- **🔒 Security**: See [README-SECURITY.md](docs/README-SECURITY.md) for security issues
- **📖 Documentation**: Browse the [docs/](docs/) folder for detailed guides

## 🚀 What's Next?

After getting started, you might want to:

1. **🔧 Customize Templates** - Add your own presentation and document templates
2. **🔍 Enable Research** - Set up Brave Search API for automated research
3. **🖼️ Add Image Sources** - Configure Unsplash/Pixabay for more image options
4. **📊 Monitor Usage** - Set up monitoring and cost tracking
5. **🚀 Deploy to Production** - Use the automated GCP Cloud Run deployment
6. **🔒 Secure Your Setup** - Follow the security guide for production deployment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Changelog

### Version 2.0.0 (Current)
- ✨ Complete MCP server ecosystem
- 🎯 Unified content creation interface
- 🔍 Automated research integration
- ✅ Content validation system
- 🎭 Advanced workflow orchestration
- 🖼️ Enhanced image and icon generation
- 📱 Multi-format document support
- 🚀 Production-ready deployment

### Version 1.0.0
- 🎯 Initial release with basic content generation
- 📊 PowerPoint generation
- 📄 Document generation
- 🖼️ Basic image generation

## 🛠️ Troubleshooting

### Common Issues

#### Health Check Failures

**Problem**: Health checks return unhealthy status
```json
{"status": "unhealthy", "checks": {"api_keys": {"status": "unhealthy"}}}
```

**Solutions**:
1. **Missing API Keys**: Ensure all required API keys are set in environment or GCP Secret Manager
2. **Invalid API Keys**: Check keys haven't expired or been revoked
3. **Secret Manager Permissions**: Verify service account has `secretmanager.secretAccessor` role
4. **Configuration Issues**: Review `README-SECURITY.md` for proper setup

#### Deployment Issues

**Problem**: GCP Cloud Run deployment fails
```bash
ERROR: (gcloud.run.services.replace) INVALID_ARGUMENT: The request has errors
```

**Solutions**:
1. **Check PROJECT_ID**: Ensure `export PROJECT_ID="your-project-id"` is set correctly
2. **Enable APIs**: Run the GCP setup commands to enable required APIs
3. **Service Account**: Verify service account exists and has proper permissions
4. **Secrets**: Ensure all secrets exist in Secret Manager (placeholders are created automatically)

#### Performance Issues

**Problem**: Slow response times or timeouts

**Solutions**:
1. **Resource Limits**: Check Cloud Run resource allocation (CPU/Memory)
2. **Cold Starts**: Enable minimum instances: `autoscaling.knative.dev/minScale: "1"`
3. **Dependencies**: Check external API response times in `/status` endpoint
4. **Monitoring**: Review GCP Cloud Run metrics for bottlenecks

#### Security Warnings

**Problem**: Security validation failures at startup

**Solutions**:
1. **Review Security Guide**: Check `README-SECURITY.md` for complete setup
2. **Rotate API Keys**: Generate new API keys if compromised
3. **Update Secrets**: Use `gcloud secrets versions add` to update keys
4. **Validate Environment**: Ensure `.env` file is not committed to git

### Diagnostic Commands

```bash
# Check health status
curl https://your-service-url/status | jq '.'

# Test all health endpoints
for endpoint in health health/live health/ready health/startup status info; do
  echo "Testing /$endpoint"
  curl -s https://your-service-url/$endpoint | jq '.status'
done

# View Cloud Run logs
gcloud run logs read mcp-server-openai --region=us-central1

# Check secret values (will show metadata only, not actual values)
gcloud secrets describe openai-api-key

# Test deployment validation
python scripts/test-deployment.py --url https://your-service-url
```

### Performance Optimization

1. **Enable CPU Boost**: Already configured in `cloud-run-service.yaml`
2. **Optimize Scaling**: Adjust min/max instances based on traffic patterns
3. **Monitor Costs**: Use GCP Billing alerts for cost management
4. **Review Metrics**: Check response times and error rates in GCP Console

### Getting Help

- **🔒 Security Issues**: Review `README-SECURITY.md` and `DEPLOYMENT_OPTIMIZATION_SUMMARY.md`
- **📊 Monitoring**: Check `/status` endpoint for detailed diagnostics
- **🚨 Emergency**: Follow security incident procedures in `README-SECURITY.md`
- **🐛 Bugs**: Open issue in GitHub repository with health check output and logs

---

**Made with ❤️ for content creators** | **[⭐ Star on GitHub](https://github.com/adrshkr/mcp-server-openai)** | **[📖 Full Documentation](README.md)**
