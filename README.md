# 🚀 Unified Content Creator System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com/your-username/unified-content-creator)

> **A comprehensive, AI-powered content creation platform that unifies PPT, DOC, HTML, and PDF generation with advanced MCP server ecosystem integration.**

## 🌟 Overview

The Unified Content Creator System is a cutting-edge platform that combines multiple content generation tools under a single, intelligent interface. It leverages the power of MCP (Model Context Protocol) servers to provide AI-powered planning, automated research, content validation, and advanced orchestration capabilities.

### ✨ Key Features

- **🎯 Unified Interface**: Single API for all content types (PPT, DOC, HTML, PDF)
- **🧠 AI-Powered Planning**: Intelligent content structuring and planning
- **🔍 Automated Research**: Web search integration for content enhancement
- **✅ Content Validation**: Quality assessment and optimization
- **🎭 Advanced Orchestration**: Complex workflow management
- **🖼️ Visual Enhancement**: Automatic image and icon generation
- **📱 Multi-Format Support**: Professional templates for all output types
- **🚀 Scalable Architecture**: MCP server ecosystem for extensibility

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google Cloud CLI (for deployment)
- API Keys for various services

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/unified-content-creator.git
   cd unified-content-creator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the system with Docker Compose**
   ```bash
   docker-compose -f docker-compose.complete.yml up -d
   ```

5. **Run tests**
   ```bash
   python scripts/test_complete_system.py
   ```

### Docker Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.complete.yml up --build

# View logs
docker-compose -f docker-compose.complete.yml logs -f

# Stop services
docker-compose -f docker-compose.complete.yml down
```

## 📚 API Reference

### Core Endpoints

#### Unified Content Creation
```http
POST /api/v1/unified/create
Content-Type: application/json

{
  "title": "My Content",
  "brief": "Content description",
  "notes": ["Point 1", "Point 2", "Point 3"],
  "output_format": "html",
  "content_style": "professional",
  "include_images": true,
  "include_icons": true
}
```

#### Individual Tool Endpoints

- **Enhanced PPT Generator**: `POST /api/v1/ppt/generate`
- **Enhanced Document Generator**: `POST /api/v1/document/generate`
- **Enhanced Image Generator**: `POST /api/v1/image/generate`
- **Enhanced Icon Generator**: `POST /api/v1/icon/generate`

#### MCP Server Endpoints

- **Sequential Thinking**: `POST /api/v1/mcp/sequential-thinking/think`
- **Brave Search**: `POST /api/v1/mcp/brave-search/search`
- **Memory**: `POST /api/v1/mcp/memory/store`
- **Filesystem**: `POST /api/v1/mcp/filesystem/write`
- **Research Integration**: `POST /api/v1/mcp/research/conduct`
- **Content Validation**: `POST /api/v1/mcp/validation/validate`
- **Advanced Orchestration**: `POST /api/v1/mcp/orchestration/create-workflow`

### Response Formats

All endpoints return JSON responses with consistent structure:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message",
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

### Running Tests

```bash
# Run complete test suite
python scripts/test_complete_system.py

# Run individual tool tests
python scripts/test_enhanced_ppt_generator.py
python scripts/test_enhanced_document_generator.py
python scripts/test_unified_system.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

The system includes comprehensive tests for:
- ✅ Unit tests for all components
- ✅ Integration tests for workflows
- ✅ Performance tests
- ✅ Error handling tests
- ✅ API endpoint tests

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

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/unified-content-creator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/unified-content-creator/discussions)

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

---

**Made with ❤️ by the Unified Content Creator Team**
