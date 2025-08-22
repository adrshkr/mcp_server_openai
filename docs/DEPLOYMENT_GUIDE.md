# 🚀 Unified Content Creator System - Complete Deployment Guide

## 📋 Overview

This guide covers all deployment options for the Unified Content Creator System, from local development to production deployment on Google Cloud Run and Kubernetes.

## 🏗️ System Architecture

The system consists of multiple interconnected services:

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

- **Python 3.11+**
- **Docker and Docker Compose**
- **Google Cloud CLI** (for cloud deployment)
- **API Keys** for various services

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

## 🐳 Docker Deployment

### Local Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.complete.yml up --build

# View service status
docker-compose -f docker-compose.complete.yml ps

# View logs
docker-compose -f docker-compose.complete.yml logs -f

# Stop services
docker-compose -f docker-compose.complete.yml down
```

### Production Docker Compose

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale unified-content-creator=3
```

### Individual Service Deployment

```bash
# Build main service
docker build -f Dockerfile.unified -t unified-content-creator:latest .

# Build MCP servers
docker build -f Dockerfile.mcp-sequential-thinking -t mcp-sequential-thinking:latest .
docker build -f Dockerfile.mcp-brave-search -t mcp-brave-search:latest .
docker build -f Dockerfile.mcp-memory -t mcp-memory:latest .
docker build -f Dockerfile.mcp-filesystem -t mcp-filesystem:latest .
docker build -f Dockerfile.mcp-research-integration -t mcp-research-integration:latest .
docker build -f Dockerfile.mcp-content-validation -t mcp-content-validation:latest .
docker build -f Dockerfile.mcp-advanced-orchestration -t mcp-advanced-orchestration:latest .

# Run containers
docker run -d -p 8000:8000 --name unified-content-creator unified-content-creator:latest
docker run -d -p 3001:3001 --name mcp-sequential-thinking mcp-sequential-thinking:latest
docker run -d -p 3002:3002 --name mcp-brave-search mcp-brave-search:latest
docker run -d -p 3003:3003 --name mcp-memory mcp-memory:latest
docker run -d -p 3004:3004 --name mcp-filesystem mcp-filesystem:latest
docker run -d -p 3005:3005 --name mcp-research-integration mcp-research-integration:latest
docker run -d -p 3006:3006 --name mcp-content-validation mcp-content-validation:latest
docker run -d -p 3007:3007 --name mcp-advanced-orchestration mcp-advanced-orchestration:latest
```

## ☁️ Google Cloud Run Deployment

### Prerequisites

1. **Install Google Cloud CLI**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Windows
   # Download from https://cloud.google.com/sdk/docs/install
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Authenticate and set project**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs**
   ```bash
   gcloud services enable \
       cloudbuild.googleapis.com \
       run.googleapis.com \
       container.googleapis.com \
       compute.googleapis.com \
       iam.googleapis.com \
       secretmanager.googleapis.com \
       monitoring.googleapis.com \
       logging.googleapis.com
   ```

### Automated Deployment

Use the comprehensive deployment script:

```bash
# Make script executable
chmod +x scripts/deploy-complete-system.sh

# Run deployment
./scripts/deploy-complete-system.sh
```

### Manual Deployment

1. **Set up service account**
   ```bash
   # Create service account
   gcloud iam service-accounts create unified-content-creator-sa \
       --display-name="Unified Content Creator Service Account"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:unified-content-creator-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:unified-content-creator-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:unified-content-creator-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

2. **Set up secrets**
   ```bash
   # Create secrets for API keys
   echo "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
   echo "your-anthropic-api-key" | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
   echo "your-google-api-key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
   echo "your-presenton-api-key" | gcloud secrets create PRESENTON_API_KEY --data-file=-
   echo "your-unsplash-api-key" | gcloud secrets create UNSPLASH_API_KEY --data-file=-
   echo "your-stable-diffusion-api-key" | gcloud secrets create STABLE_DIFFUSION_API_KEY --data-file=-
   echo "your-pixabay-api-key" | gcloud secrets create PIXABAY_API_KEY --data-file=-
   echo "your-brave-search-api-key" | gcloud secrets create BRAVE_SEARCH_API_KEY --data-file=-
   ```

3. **Build and push images**
   ```bash
   # Build main service
   docker build -f Dockerfile.unified -t gcr.io/YOUR_PROJECT_ID/unified-content-creator:latest .
   docker push gcr.io/YOUR_PROJECT_ID/unified-content-creator:latest
   
   # Build MCP servers
   for server in sequential-thinking brave-search memory filesystem research-integration content-validation advanced-orchestration; do
       docker build -f Dockerfile.mcp-${server} -t gcr.io/YOUR_PROJECT_ID/mcp-${server}:latest .
       docker push gcr.io/YOUR_PROJECT_ID/mcp-${server}:latest
   done
   ```

4. **Deploy to Cloud Run**
   ```bash
   # Deploy main service
   gcloud run deploy unified-content-creator \
       --image gcr.io/YOUR_PROJECT_ID/unified-content-creator:latest \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated \
       --service-account="unified-content-creator-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --memory 2Gi \
       --cpu 2 \
       --timeout 300 \
       --max-instances 10 \
       --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO" \
       --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest,PRESENTON_API_KEY=PRESENTON_API_KEY:latest,UNSPLASH_API_KEY=UNSPLASH_API_KEY:latest,STABLE_DIFFUSION_API_KEY=STABLE_DIFFUSION_API_KEY:latest,PIXABAY_API_KEY=PIXABAY_API_KEY:latest,BRAVE_SEARCH_API_KEY=BRAVE_SEARCH_API_KEY:latest"
   
   # Deploy MCP servers
   for server in sequential-thinking brave-search memory filesystem research-integration content-validation advanced-orchestration; do
       gcloud run deploy mcp-${server} \
           --image gcr.io/YOUR_PROJECT_ID/mcp-${server}:latest \
           --platform managed \
           --region us-central1 \
           --allow-unauthenticated \
           --service-account="unified-content-creator-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
           --memory 1Gi \
           --cpu 1 \
           --timeout 120 \
           --max-instances 5
   done
   ```

## ☸️ Kubernetes Deployment

### Prerequisites

1. **Install kubectl**
   ```bash
   # macOS
   brew install kubectl
   
   # Windows
   # Download from https://kubernetes.io/docs/tasks/tools/install-kubectl/
   
   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

2. **Set up cluster access**
   ```bash
   # For GKE
   gcloud container clusters get-credentials YOUR_CLUSTER_NAME --region YOUR_REGION
   
   # For other clusters
   kubectl config set-cluster YOUR_CLUSTER_NAME --server=https://YOUR_CLUSTER_IP
   kubectl config set-credentials YOUR_USER --token=YOUR_TOKEN
   kubectl config set-context YOUR_CONTEXT --cluster=YOUR_CLUSTER_NAME --user=YOUR_USER
   kubectl config use-context YOUR_CONTEXT
   ```

### Deploy to Kubernetes

1. **Create namespace**
   ```bash
   kubectl create namespace unified-content
   ```

2. **Apply Kubernetes manifests**
   ```bash
   # Apply all manifests
   kubectl apply -f k8s/ -n unified-content
   
   # Check deployment status
   kubectl get pods -n unified-content
   kubectl get services -n unified-content
   kubectl get deployments -n unified-content
   ```

3. **Monitor deployment**
   ```bash
   # View logs
   kubectl logs -f deployment/unified-content-creator -n unified-content
   
   # Check service health
   kubectl get endpoints -n unified-content
   
   # Port forward for local access
   kubectl port-forward service/unified-content-creator 8000:8000 -n unified-content
   ```

## 🔧 Configuration

### Environment Variables

**Required:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

**Optional:**
```bash
export PRESENTON_API_KEY="your-presenton-api-key"
export UNSPLASH_API_KEY="your-unsplash-api-key"
export STABLE_DIFFUSION_API_KEY="your-stable-diffusion-api-key"
export PIXABAY_API_KEY="your-pixabay-api-key"
export BRAVE_SEARCH_API_KEY="your-brave-search-api-key"
```

### Configuration Files

- **Main Config**: `config/unified_system_complete.yaml`
- **Tool Configs**: `config/enhanced_*.yaml`
- **Docker Config**: `docker-compose.complete.yml`

### Custom Configuration

Create custom configuration files:

```yaml
# config/custom.yaml
system:
  name: "Custom Content Creator"
  environment: "production"
  debug: false

content_generation:
  enhanced_ppt_generator:
    enabled: true
    default_model: "gpt-4o"
    max_slides: 100
    
  enhanced_document_generator:
    enabled: true
    default_format: "html"
    templates: ["custom", "branded"]
```

## 📊 Monitoring and Logging

### Health Checks

```bash
# Main system health
curl http://localhost:8000/health

# MCP server health
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
curl http://localhost:3004/health
curl http://localhost:3005/health
curl http://localhost:3006/health
curl http://localhost:3007/health
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# System information
curl http://localhost:8000/info
```

### Logging

```bash
# View logs
docker-compose -f docker-compose.complete.yml logs -f

# View specific service logs
docker-compose -f docker-compose.complete.yml logs -f unified-content-creator
docker-compose -f docker-compose.complete.yml logs -f mcp-sequential-thinking
```

## 🔒 Security

### Authentication

```bash
# Enable API key authentication
export API_KEY="your-secure-api-key"

# Update configuration
echo "security:
  authentication:
    enabled: true
    type: api_key
    api_key_env: API_KEY" >> config/unified_system_complete.yaml
```

### Network Security

```bash
# Restrict access to specific IPs
echo "security:
  network:
    allowed_ips:
      - 192.168.1.0/24
      - 10.0.0.0/8" >> config/unified_system_complete.yaml
```

### SSL/TLS

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update Nginx configuration
echo "server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of configuration
}" >> nginx/nginx.conf
```

## 🚀 Performance Optimization

### Scaling

```bash
# Scale services horizontally
docker-compose -f docker-compose.complete.yml up -d --scale unified-content-creator=3

# Kubernetes scaling
kubectl scale deployment unified-content-creator --replicas=5 -n unified-content
```

### Caching

```bash
# Enable Redis caching
docker-compose -f docker-compose.complete.yml up -d redis

# Update configuration
echo "performance:
  caching:
    enabled: true
    redis_url: redis://redis:6379" >> config/unified_system_complete.yaml
```

### Load Balancing

```bash
# Start Nginx load balancer
docker-compose -f docker-compose.complete.yml up -d nginx

# Check load balancer status
curl http://localhost/health
```

## 🧪 Testing

### Pre-deployment Testing

```bash
# Run comprehensive tests
python scripts/test_complete_system.py

# Run specific tool tests
python scripts/test_enhanced_ppt_generator.py
python scripts/test_enhanced_document_generator.py
python scripts/test_unified_system.py
```

### Post-deployment Testing

```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:3001/health

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/unified/create \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","brief":"Test brief","notes":["Test note"],"output_format":"html"}'
```

### Load Testing

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/health
```

## 🔄 Updates and Maintenance

### Updating Services

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.complete.yml down
docker-compose -f docker-compose.complete.yml up --build -d
```

### Rolling Updates (Kubernetes)

```bash
# Update deployment
kubectl set image deployment/unified-content-creator \
  unified-content-creator=gcr.io/YOUR_PROJECT_ID/unified-content-creator:latest \
  -n unified-content

# Check rollout status
kubectl rollout status deployment/unified-content-creator -n unified-content
```

### Backup and Recovery

```bash
# Backup data
docker exec mcp-memory sqlite3 /app/data/memory.db ".backup /app/data/backup_$(date +%Y%m%d_%H%M%S).db"

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz config/
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.complete.yml logs unified-content-creator
   
   # Check environment variables
   docker-compose -f docker-compose.complete.yml config
   ```

2. **MCP servers not responding**
   ```bash
   # Check network connectivity
   docker exec unified-content-creator ping mcp-sequential-thinking
   
   # Check service status
   docker-compose -f docker-compose.complete.yml ps
   ```

3. **API key errors**
   ```bash
   # Verify secrets
   gcloud secrets list
   
   # Check secret values
   gcloud secrets versions access latest --secret="OPENAI_API_KEY"
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart services
docker-compose -f docker-compose.complete.yml restart
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Monitor system metrics
curl http://localhost:8000/metrics | grep -E "(cpu|memory|requests)"
```

## 📚 Additional Resources

- **Architecture Documentation**: [docs/TOOL_ARCHITECTURE_WORKFLOW.md](docs/TOOL_ARCHITECTURE_WORKFLOW.md)
- **API Reference**: [README.md](README.md)
- **Configuration Guide**: [config/unified_system_complete.yaml](config/unified_system_complete.yaml)
- **Testing Guide**: [scripts/test_complete_system.py](scripts/test_complete_system.py)

## 🤝 Support

- **GitHub Issues**: [Create an issue](https://github.com/your-username/unified-content-creator/issues)
- **Documentation**: [docs/](docs/)
- **Community**: [GitHub Discussions](https://github.com/your-username/unified-content-creator/discussions)

---

**Happy Deploying! 🚀**
