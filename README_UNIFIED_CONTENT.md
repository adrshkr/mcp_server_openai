# 🚀 **Unified Content Creator Tool**

A comprehensive, AI-powered content creation solution that integrates multiple MCP servers to generate high-quality content across multiple formats: **PPT**, **DOC**, **PDF**, and **HTML**.

## ✨ **Features**

### 🎯 **Multi-Format Content Generation**
- **PowerPoint Presentations**: Professional slides with enhanced visuals
- **Word Documents**: Rich text documents with embedded images and icons
- **PDF Documents**: Print-ready documents with consistent formatting
- **HTML Content**: Web-ready, responsive content for digital platforms

### 🧠 **AI-Powered Content Enhancement**
- **Sequential Thinking**: Intelligent content planning and structure
- **Research Integration**: Web search for fact-checking and enrichment
- **Context Management**: Memory-based learning and adaptation
- **Visual Enhancement**: AI-generated images and icons

### 🖼️ **Advanced Visual Generation**
- **Multi-Provider Images**: Unsplash, Stable Diffusion, Pixabay
- **Smart Icon Generation**: Business, technology, creative, educational themes
- **Content-Aware Selection**: AI-powered visual matching
- **Fallback Strategies**: Automatic provider switching

### 🌍 **Global & Professional**
- **Multi-language Support**: 7+ languages including RTL support
- **Professional Templates**: Business, academic, creative, technical styles
- **Brand Consistency**: Custom branding and white-label options
- **Enterprise Features**: Advanced security, monitoring, and scaling

## 🏗️ **Architecture**

### **MCP Server Integration**
```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Content Creator                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Sequential  │ │   Brave     │ │   Memory    │          │
│  │  Thinking   │ │   Search    │ │   Server    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Filesystem  │ │   Image     │ │    Icon     │          │
│  │   Server    │ │ Generation  │ │ Generation  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### **Content Creation Pipeline**
```
User Input → MCP Planning → Research → Content Generation → 
Visual Enhancement → Format Rendering → Output Delivery
```

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Required tools
- Python 3.11+
- Docker & Docker Compose
- Google Cloud CLI (for deployment)
- Git

# API Keys (set as environment variables)
- UNSPLASH_API_KEY
- STABLE_DIFFUSION_API_KEY
- PIXABAY_API_KEY
- CUSTOM_ICON_API_KEY
- BRAVE_API_KEY
```

### **2. Local Development Setup**
```bash
# Clone the repository
git clone <repository-url>
cd mcp_server_openai

# Install dependencies
uv pip install -r requirements.txt

# Start all services with Docker Compose
docker-compose up -d

# Run the demo
uv run python scripts/demo_unified_content.py
```

### **3. Basic Usage**
```python
from mcp_server_openai.tools.unified_content_creator import create_unified_content

# Create a presentation
result = await create_unified_content(
    title="AI in Business",
    brief="Exploring AI applications in modern business",
    notes=["Automation", "Analytics", "Customer Service"],
    output_format="presentation",
    content_style="professional",
    include_images=True,
    include_icons=True
)

print(f"Created: {result.file_path}")
```

## 📚 **API Reference**

### **Main Function**
```python
async def create_unified_content(
    title: str,                    # Content title
    brief: str,                    # Brief description
    notes: List[str],              # Content notes/points
    output_format: str = "presentation",  # presentation, document, pdf, html
    content_style: str = "professional",  # professional, creative, modern, classic, minimalist
    language: str = "English",     # Content language
    theme: str = "auto",           # auto, business, technology, creative, educational
    include_images: bool = True,   # Generate/select images
    include_icons: bool = True,    # Generate/select icons
    target_length: Optional[str] = None,  # Target content length
    custom_template: Optional[str] = None,  # Custom template
    branding: Optional[Dict[str, Any]] = None,  # Custom branding
    client_id: Optional[str] = None  # Client identifier
) -> ContentResult
```

### **MCP Tools**
```python
# Enhanced Image Generation
enhanced_image_generate(query, content_type, style, count, format, quality, size)
enhanced_image_content_aware(content, content_type, count)
enhanced_image_optimize(image_url, target_format, target_size)

# Enhanced Icon Generation
enhanced_icon_generate(description, content_type, style, format, size, color_scheme, theme, count)
enhanced_icon_content_aware(content, content_type, count)
enhanced_icon_suggestions(content, content_type)

# Unified Content Creation
unified_content_create(title, brief, notes, output_format, content_style, language, theme, include_images, include_icons, target_length, custom_template, branding, client_id)
unified_content_formats()
unified_content_status(client_id)
```

## 🐳 **Docker Deployment**

### **Local Development**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Production Deployment**
```bash
# Deploy to Google Cloud Run
PROJECT_ID=your-project-id ./scripts/deploy-unified-to-cloud-run.sh

# Or deploy individual services
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ **Google Cloud Run Deployment**

### **1. Prerequisites**
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### **2. Deploy**
```bash
# Set environment variables
export PROJECT_ID="your-project-id"
export UNSPLASH_API_KEY="your-unsplash-key"
export STABLE_DIFFUSION_API_KEY="your-stable-diffusion-key"
export PIXABAY_API_KEY="your-pixabay-key"
export CUSTOM_ICON_API_KEY="your-custom-icon-key"
export BRAVE_API_KEY="your-brave-key"

# Run deployment script
chmod +x scripts/deploy-unified-to-cloud-run.sh
./scripts/deploy-unified-to-cloud-run.sh
```

### **3. Service URLs**
After deployment, your services will be available at:
- **Main Service**: `https://unified-content-creator-{hash}.run.app`
- **Image Generation**: `https://mcp-image-generation-{hash}.run.app`
- **Icon Generation**: `https://mcp-icon-generation-{hash}.run.app`
- **MCP Servers**: Various endpoints for different MCP services

## 🔧 **Configuration**

### **Environment Variables**
```bash
# API Keys
UNSPLASH_API_KEY=your_unsplash_key
STABLE_DIFFUSION_API_KEY=your_stable_diffusion_key
PIXABAY_API_KEY=your_pixabay_key
CUSTOM_ICON_API_KEY=your_custom_icon_key
BRAVE_API_KEY=your_brave_key

# Service URLs
PRESENTON_API_URL=http://localhost:3000
MCP_SEQUENTIAL_THINKING_URL=http://localhost:3001
MCP_BRAVE_SEARCH_URL=http://localhost:3002
MCP_MEMORY_URL=http://localhost:3003
MCP_FILESYSTEM_URL=http://localhost:3004

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### **Configuration Files**
- `config/unified_content.yaml` - Main configuration
- `config/enhanced_ppt.yaml` - PPT generation settings
- `config/enhanced_ppt.yaml` - Enhanced PPT settings

## 📊 **Monitoring & Logging**

### **Health Checks**
```bash
# Main service
curl https://your-service.run.app/health

# MCP servers
curl https://mcp-image-generation.run.app/health
curl https://mcp-icon-generation.run.app/health
```

### **Metrics**
- Content creation requests
- Processing time
- Success/failure rates
- Resource usage
- API response times

### **Logs**
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Filter by service
gcloud logging read "resource.labels.service_name=unified-content-creator"
```

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_unified_content_creator.py -v
uv run pytest tests/test_enhanced_image_generator.py -v
uv run pytest tests/test_enhanced_icon_generator.py -v
```

### **Integration Tests**
```bash
# Test with real MCP servers
docker-compose up -d
uv run pytest tests/test_integration.py -v
```

### **Demo Scripts**
```bash
# Run unified content creator demo
uv run python scripts/demo_unified_content.py

# Run enhanced PPT demo
uv run python scripts/demo_enhanced_ppt.py
```

## 🔒 **Security & Privacy**

### **Authentication**
- API key-based authentication
- Service account permissions
- Rate limiting (60 requests/minute)
- Request validation

### **Data Privacy**
- 30-day data retention
- Anonymized logging
- Secure API key storage
- No persistent user data

### **Network Security**
- HTTPS enforcement
- CORS configuration
- Input sanitization
- SQL injection prevention

## 📈 **Performance & Scaling**

### **Resource Limits**
- **Memory**: 2GB per instance
- **CPU**: 2 vCPUs per instance
- **Concurrency**: 80 requests per instance
- **Timeout**: 15 minutes per request

### **Auto-scaling**
- **Min Instances**: 1 (always running)
- **Max Instances**: 10 (auto-scale up)
- **Scaling**: Based on CPU and memory usage

### **Optimization**
- Response caching (1 hour TTL)
- Parallel processing (5 concurrent requests)
- Image optimization and compression
- Lazy loading for large content

## 🌟 **Use Cases**

### **Business & Enterprise**
- **Sales Presentations**: Professional slides with company branding
- **Business Reports**: Comprehensive documents with data visualization
- **Training Materials**: Educational content with visual aids
- **Marketing Content**: Creative materials for campaigns

### **Education & Training**
- **Course Materials**: Structured learning content
- **Presentations**: Academic and training presentations
- **Documentation**: Technical and user guides
- **Assessment Materials**: Quizzes and evaluations

### **Creative & Design**
- **Portfolio Presentations**: Showcase creative work
- **Design Documentation**: Process and methodology guides
- **Creative Briefs**: Project specifications and requirements
- **Visual Content**: Social media and marketing materials

### **Technology & Development**
- **Technical Documentation**: API docs and user manuals
- **Project Presentations**: Development updates and demos
- **Architecture Diagrams**: System design documentation
- **Training Guides**: Developer onboarding materials

## 🔮 **Roadmap & Future Features**

### **Phase 1 (Current)**
- ✅ Multi-format content generation
- ✅ MCP server integration
- ✅ Enhanced image and icon generation
- ✅ Google Cloud Run deployment

### **Phase 2 (Next)**
- 🔄 Advanced AI content analysis
- 🔄 Custom template engine
- 🔄 Collaborative editing
- 🔄 Version control and history

### **Phase 3 (Future)**
- 📋 Real-time collaboration
- 📋 Advanced analytics dashboard
- 📋 Custom AI model training
- 📋 Enterprise SSO integration

## 🤝 **Contributing**

### **Development Setup**
```bash
# Fork and clone
git clone https://github.com/your-username/mcp_server_openai.git
cd mcp_server_openai

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### **Code Quality**
- **Formatting**: Black
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Testing**: Pytest with 90%+ coverage

### **Pull Request Process**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Ensure all tests pass
6. Submit a pull request

## 📞 **Support & Community**

### **Documentation**
- **API Docs**: Available at `/docs` endpoint
- **Examples**: See `scripts/` directory
- **Configuration**: See `config/` directory

### **Issues & Questions**
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Wiki**: Additional documentation and guides

### **Community**
- **Discord**: Join our community server
- **Slack**: Connect with other developers
- **Meetups**: Local and virtual events

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **MCP Community**: For the Model Context Protocol standard
- **Presenton**: For PowerPoint generation capabilities
- **OpenAI, Anthropic, Google**: For LLM integration
- **Unsplash, Pixabay**: For stock image APIs
- **Iconify, Lucide**: For icon libraries

---

**Made with ❤️ by the Unified Content Creator Team**

*Transform your content creation workflow with AI-powered intelligence and MCP server integration.*

