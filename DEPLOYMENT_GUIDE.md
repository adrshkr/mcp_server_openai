# 🚀 Enhanced PPT Generator - Deployment Guide

This guide provides comprehensive instructions for deploying the Enhanced PPT Generator tool, which combines our MCP server infrastructure with advanced LLM preprocessing and the Presenton API for high-quality PowerPoint generation.

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Local Development Setup](#-local-development-setup)
- [Docker Deployment](#-docker-deployment)
- [Google Cloud Run Deployment](#-google-cloud-run-deployment)
- [Environment Configuration](#-environment-configuration)
- [Testing and Validation](#-testing-and-validation)
- [Monitoring and Troubleshooting](#-monitoring-and-troubleshooting)

## 🔧 Prerequisites

### Required Software
- **Python 3.11+** with pip/uv
- **Docker** (for containerized deployment)
- **Google Cloud CLI** (for Cloud Run deployment)
- **Git** (for version control)

### Required Accounts & APIs
- **OpenAI API Key** (for GPT models)
- **Anthropic API Key** (for Claude models)
- **Google API Key** (for Gemini models)
- **Presenton API Access** (for PPT generation)
- **Google Cloud Project** (for Cloud Run deployment)

### System Requirements
- **Memory**: Minimum 2GB RAM, Recommended 4GB+
- **Storage**: Minimum 1GB free space
- **Network**: Stable internet connection for API calls

## 🏠 Local Development Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp_server_openai

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install langchain-openai langchain-anthropic langchain-google-genai langchain-core python-dotenv requests
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Presenton API Configuration
PRESENTON_API_URL=https://your-presenton-service.com

# MCP Server Configuration
MCP_CONFIG_PATH=./config
MCP_MONITORING_ENABLED=true
MCP_COST_HOURLY_MAX=50.0
MCP_COST_DAILY_MAX=500.0
```

### 3. Configuration Files

Ensure the configuration files are in place:

```bash
# Enhanced PPT Generator config
config/enhanced_ppt.yaml

# Enhanced Content Creator config (if using)
config/enhanced_content.yaml
```

### 4. Test Local Setup

```bash
# Run the demo script
uv run python scripts/demo_enhanced_ppt.py

# Run tests
uv run pytest tests/test_enhanced_ppt_generator.py -v

# Start the MCP server
uv run mcp dev src/mcp_server_openai/server.py:app
```

## 🐳 Docker Deployment

### 1. Build Docker Image

```bash
# Build using the enhanced Dockerfile
docker build -f Dockerfile.enhanced -t enhanced-ppt-generator:latest .

# Tag for registry (if pushing to registry)
docker tag enhanced-ppt-generator:latest your-registry/enhanced-ppt-generator:latest
```

### 2. Run Docker Container

```bash
# Run with environment variables
docker run -d \
  --name enhanced-ppt-generator \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  -e PRESENTON_API_URL=https://your-service.com \
  -v $(pwd)/output:/app/output \
  enhanced-ppt-generator:latest

# Or use docker-compose
docker-compose up -d
```

### 3. Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  enhanced-ppt-generator:
    build:
      context: .
      dockerfile: Dockerfile.enhanced
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PRESENTON_API_URL=${PRESENTON_API_URL}
      - MCP_MONITORING_ENABLED=true
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## ☁️ Google Cloud Run Deployment

### 1. Initial Setup

```bash
# Install Google Cloud CLI (if not already installed)
# https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login

# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build and Push Image

```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Build and tag image
docker build -f Dockerfile.enhanced -t gcr.io/$PROJECT_ID/enhanced-ppt-generator:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/enhanced-ppt-generator:latest
```

### 3. Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy enhanced-ppt-generator \
  --image gcr.io/$PROJECT_ID/enhanced-ppt-generator:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80 \
  --max-instances 10 \
  --set-env-vars PRESENTON_API_URL=https://your-presenton-service.com \
  --set-env-vars MCP_MONITORING_ENABLED=true \
  --set-env-vars MCP_COST_HOURLY_MAX=50.0 \
  --set-env-vars MCP_COST_DAILY_MAX=500.0
```

### 4. Automated Deployment Script

Use the provided deployment script:

```bash
# Make script executable
chmod +x scripts/deploy-to-cloud-run.sh

# Set environment variables and deploy
export PROJECT_ID=your-project-id
export REGION=us-central1
export PRESENTON_API_URL=https://your-presenton-service.com

# Optional: Set API keys for automatic secrets setup
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
export GOOGLE_API_KEY=your_google_key

# Run deployment
./scripts/deploy-to-cloud-run.sh
```

### 5. Set Up API Key Secrets

```bash
# Create secrets for API keys
echo "your_openai_api_key" | gcloud secrets create openai-api-key --data-file=-
echo "your_anthropic_api_key" | gcloud secrets create anthropic-api-key --data-file=-
echo "your_google_api_key" | gcloud secrets create google-api-key --data-file=-

# Update service to use secrets
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --update-secrets OPENAI_API_KEY=openai-api-key:latest \
  --update-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest \
  --update-secrets GOOGLE_API_KEY=google-api-key:latest
```

## ⚙️ Environment Configuration

### Configuration File Structure

The enhanced PPT generator uses a hierarchical configuration system:

```yaml
# config/enhanced_ppt.yaml
enhanced_ppt:
  presenton_api:
    base_url: "${PRESENTON_API_URL}"
    timeout: 60
    max_retries: 3
  
  llm_models:
    openai:
      default_model: "gpt-4o"
      max_tokens: 2000
      temperature: 0.2
    
    anthropic:
      default_model: "claude-3-5-sonnet"
      max_tokens: 2000
      temperature: 0.2
    
    google:
      default_model: "gemini-1.5-pro"
      max_tokens: 2000
      temperature: 0.2
  
  templates:
    classic: # Academic presentations
    general: # Business presentations
    modern:  # Creative presentations
    professional: # Corporate presentations
```

### Client-Specific Overrides

```yaml
clients:
  enterprise:
    enhanced_ppt:
      template_preference: "professional"
      include_images: false
      max_slides: 12
  
  startup:
    enhanced_ppt:
      template_preference: "modern"
      include_images: true
      max_slides: 10
```

### Environment Variables Priority

1. **Environment Variables** (highest priority)
2. **Client-specific overrides**
3. **Configuration file defaults**
4. **Code defaults** (lowest priority)

## 🧪 Testing and Validation

### 1. Health Check

```bash
# Test health endpoint
curl https://your-service-url/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### 2. API Endpoints Testing

```bash
# Test PPT generation
curl -X POST https://your-service-url/api/v1/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "notes": ["Topic: AI Strategy", "Market analysis"],
    "brief": "Create a presentation about AI strategy",
    "target_length": "8 slides",
    "template_preference": "professional"
  }'

# Test content analysis
curl -X POST https://your-service-url/api/v1/ppt/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "notes": ["Topic: AI Strategy", "Market analysis"],
    "brief": "Analyze content for AI strategy presentation",
    "target_length": "8 slides"
  }'

# Test templates endpoint
curl https://your-service-url/api/v1/ppt/templates
```

### 3. Load Testing

```bash
# Install Apache Bench (ab)
# On Ubuntu: sudo apt-get install apache2-utils
# On macOS: brew install httpd

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -T application/json \
  -p test_payload.json \
  https://your-service-url/api/v1/ppt/generate
```

## 📊 Monitoring and Troubleshooting

### 1. Service Monitoring

```bash
# Check service status
gcloud run services describe enhanced-ppt-generator --region us-central1

# View logs
gcloud logs read --service=enhanced-ppt-generator --limit=50

# Monitor metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

### 2. Common Issues and Solutions

#### Issue: Service fails to start
```bash
# Check container logs
gcloud run services logs read enhanced-ppt-generator --region us-central1

# Verify environment variables
gcloud run services describe enhanced-ppt-generator --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

#### Issue: API key authentication fails
```bash
# Verify secrets exist
gcloud secrets list

# Check secret values (be careful with this in production)
gcloud secrets versions access latest --secret="openai-api-key"
```

#### Issue: High memory usage
```bash
# Scale up memory
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --memory 8Gi

# Or scale down concurrency
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --concurrency 40
```

### 3. Performance Optimization

```bash
# Enable CPU allocation
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --cpu-throttling=false \
  --startup-cpu-boost=true

# Adjust scaling parameters
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --min-instances=1 \
  --max-instances=20
```

## 🔒 Security Considerations

### 1. API Key Management
- Use Google Secret Manager for API keys
- Rotate keys regularly
- Monitor API usage and costs

### 2. Network Security
- Use HTTPS only
- Configure CORS appropriately
- Implement rate limiting

### 3. Access Control
- Use IAM roles for service accounts
- Implement proper authentication if needed
- Monitor access logs

## 📈 Scaling and Performance

### 1. Auto-scaling Configuration
```bash
# Configure auto-scaling
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --min-instances=1 \
  --max-instances=50 \
  --concurrency=100
```

### 2. Resource Optimization
```bash
# Optimize resource allocation
gcloud run services update enhanced-ppt-generator \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --timeout 600
```

### 3. CDN and Edge Locations
```bash
# Enable Cloud CDN (if applicable)
gcloud compute backend-services update enhanced-ppt-generator \
  --enable-cdn \
  --global
```

## 🚀 Next Steps

### 1. Production Deployment
- Set up monitoring and alerting
- Implement CI/CD pipelines
- Configure backup and disaster recovery

### 2. Advanced Features
- Implement caching strategies
- Add authentication and authorization
- Set up multi-region deployment

### 3. Integration
- Connect with existing systems
- Implement webhook notifications
- Add analytics and reporting

## 📞 Support and Resources

### Documentation
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [MCP Server Documentation](https://modelcontextprotocol.io/)
- [Presenton API Documentation](https://presenton.com/docs)

### Community
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/enhanced-ppt-generator)

### Monitoring Tools
- [Google Cloud Monitoring](https://cloud.google.com/monitoring)
- [Google Cloud Logging](https://cloud.google.com/logging)
- [Google Cloud Trace](https://cloud.google.com/trace)

---

**🎉 Congratulations!** You've successfully deployed the Enhanced PPT Generator. The service is now ready to generate high-quality PowerPoint presentations using advanced LLM preprocessing and the Presenton API.

