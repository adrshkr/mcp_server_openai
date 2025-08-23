# 🚀 MCP Server OpenAI - AI Content Creation Platform

> **Create professional presentations, documents, and web content with AI-powered tools**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com/adrshkr/mcp-server-openai)

## 🎯 What This Does

**MCP Server OpenAI** is an AI-powered content creation platform that helps you generate:

- 📊 **PowerPoint Presentations** - Professional slides with images and icons
- 📄 **Documents** - Word docs, PDFs, HTML pages with smart formatting  
- 🖼️ **Images & Icons** - AI-generated visuals that match your content
- 🔍 **Research-Enhanced Content** - Automatically researched and fact-checked

**Perfect for:** Business professionals, educators, content creators, and anyone who needs to create professional content quickly.

## ⚡ Quick Start (5 Minutes)

### 1. **Prerequisites**
- Python 3.11+ installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### 2. **Install & Setup**
```bash
# Clone the project
git clone https://github.com/adrshkr/mcp-server-openai.git
cd mcp-server-openai

# Install dependencies (fast with uv)
pip install uv
uv sync

# Set up your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### 3. **Start the Server**
```bash
# Start the HTTP server
python -m mcp_server_openai --http --port 8000

# Or use the optimized startup
python scripts/utilities/startup.py
```

### 4. **Test It Works**
```bash
# Check server health
curl http://localhost:8000/health

# Create your first presentation
curl -X POST http://localhost:8000/api/v1/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "notes": ["Introduction to AI", "Benefits of automation", "Future outlook"],
    "brief": "AI presentation for business meeting",
    "target_length": "5-7 slides"
  }'
```

## 🛠️ What You Can Build

### **Create Presentations**
```bash
POST /api/v1/ppt/generate
{
  "notes": ["Market analysis", "Growth projections", "Recommendations"],
  "brief": "Q4 business review presentation",
  "template_preference": "professional",
  "include_images": true
}
```

### **Generate Documents**
```bash
POST /api/v1/document/generate
{
  "title": "Project Report",
  "content": "# Executive Summary\n\nProject overview...",
  "output_format": "pdf",
  "template": "corporate"
}
```

### **Create Images**
```bash
POST /api/v1/image/generate
{
  "query": "modern office workspace",
  "style": "professional",
  "format": "jpeg"
}
```

## 🎨 Available Tools

| Tool | What It Does | Best For |
|------|-------------|----------|
| **PPT Generator** | Creates PowerPoint presentations | Business meetings, education |
| **Document Generator** | Creates Word/PDF/HTML documents | Reports, manuals, web pages |
| **Image Generator** | Finds/creates relevant images | Visual content, presentations |
| **Icon Generator** | Creates matching icons | UI elements, infographics |
| **Content Planner** | AI-powered content structuring | Complex projects, research |

## 🌐 Deploy to Production

### **Option 1: Google Cloud Run (Recommended)**
```bash
# One-command deployment
./deployment/scripts/deploy-optimized.sh

# Your server will be live at: https://your-service-url
```

### **Option 2: Docker**
```bash
# Build and run with Docker
docker build -t mcp-server .
docker run -p 8000:8000 --env-file .env mcp-server
```

### **Option 3: Local Production**
```bash
# Run with production settings
uvicorn mcp_server_openai.api.http_server:app \
  --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Health & Monitoring

Your server includes built-in monitoring:

- **Health Check**: `GET /health` - Basic server status
- **Detailed Status**: `GET /status` - Full system diagnostics  
- **Service Info**: `GET /info` - Available endpoints
- **Metrics**: `GET /metrics` - Performance data

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
```

### **API Errors**
```bash
# Check server health
curl http://localhost:8000/status

# View logs
tail -f logs/mcp_server.log
```

### **Performance Issues**
- Increase memory: Set `--workers 1` for single worker
- Check API limits: Monitor your OpenAI usage
- Enable caching: Set `CACHE_ENABLED=true`

## 📚 Learn More

- **[Full Documentation](docs/)** - Complete guides and API reference
- **[Security Guide](docs/README-SECURITY.md)** - Production security setup
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Advanced deployment options
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/adrshkr/mcp-server-openai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adrshkr/mcp-server-openai/discussions)
- **Security**: See [README-SECURITY.md](docs/README-SECURITY.md)

---

**Made with ❤️ for content creators** | **[View Full Documentation →](README.md)**
