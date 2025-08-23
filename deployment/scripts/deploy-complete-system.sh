#!/bin/bash

# 🚀 Unified Content Creator System - Complete Deployment Script
# This script deploys the entire system including all MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="unified-content-creator"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "your-project-id")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "Google Cloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if kubectl is installed (optional)
    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl is not installed. Kubernetes deployment will be skipped."
        KUBERNETES_ENABLED=false
    else
        KUBERNETES_ENABLED=true
    fi

    log_success "Prerequisites check completed"
}

setup_environment() {
    log_info "Setting up environment..."

    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please update .env file with your API keys and configuration"
    fi

    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi

    # Create necessary directories
    mkdir -p output data logs templates cache monitoring/grafana monitoring/prometheus nginx

    log_success "Environment setup completed"
}

enable_apis() {
    log_info "Enabling required Google Cloud APIs..."

    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        container.googleapis.com \
        compute.googleapis.com \
        iam.googleapis.com \
        secretmanager.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com

    log_success "Google Cloud APIs enabled"
}

setup_service_account() {
    log_info "Setting up service account..."

    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe "${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
        gcloud iam service-accounts create "${PROJECT_NAME}-sa" \
            --display-name="Unified Content Creator Service Account"
    fi

    # Grant necessary permissions
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/run.admin"

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.admin"

    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"

    log_success "Service account setup completed"
}

setup_secrets() {
    log_info "Setting up secrets..."

    # Create secrets for API keys
    for secret in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY PRESENTON_API_KEY UNSPLASH_API_KEY STABLE_DIFFUSION_API_KEY PIXABAY_API_KEY BRAVE_SEARCH_API_KEY; do
        if [ ! -z "${!secret}" ]; then
            if ! gcloud secrets describe "$secret" &>/dev/null; then
                echo "${!secret}" | gcloud secrets create "$secret" --data-file=-
                log_info "Created secret: $secret"
            else
                echo "${!secret}" | gcloud secrets versions add "$secret" --data-file=-
                log_info "Updated secret: $secret"
            fi
        fi
    done

    log_success "Secrets setup completed"
}

build_and_push_images() {
    log_info "Building and pushing Docker images..."

    # Build main unified system image
    docker build -f Dockerfile.unified -t gcr.io/${PROJECT_ID}/${PROJECT_NAME}:latest .
    docker push gcr.io/${PROJECT_ID}/${PROJECT_NAME}:latest

    # Build MCP server images
    for server in sequential-thinking brave-search memory filesystem research-integration content-validation advanced-orchestration; do
        if [ -f "Dockerfile.mcp-${server}" ]; then
            docker build -f Dockerfile.mcp-${server} -t gcr.io/${PROJECT_ID}/mcp-${server}:latest .
            docker push gcr.io/${PROJECT_ID}/mcp-${server}:latest
        fi
    done

    log_success "Docker images built and pushed"
}

deploy_to_cloud_run() {
    log_info "Deploying to Google Cloud Run..."

    # Deploy main unified system
    gcloud run deploy ${PROJECT_NAME} \
        --image gcr.io/${PROJECT_ID}/${PROJECT_NAME}:latest \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --service-account="${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --max-instances 10 \
        --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO" \
        --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest,PRESENTON_API_KEY=PRESENTON_API_KEY:latest,UNSPLASH_API_KEY=UNSPLASH_API_KEY:latest,STABLE_DIFFUSION_API_KEY=STABLE_DIFFUSION_API_KEY:latest,PIXABAY_API_KEY=PIXABAY_API_KEY:latest,BRAVE_SEARCH_API_KEY=BRAVE_SEARCH_API_KEY:latest"

    # Deploy MCP servers
    for server in sequential-thinking brave-search memory filesystem research-integration content-validation advanced-orchestration; do
        if [ -f "Dockerfile.mcp-${server}" ]; then
            gcloud run deploy mcp-${server} \
                --image gcr.io/${PROJECT_ID}/mcp-${server}:latest \
                --platform managed \
                --region ${REGION} \
                --allow-unauthenticated \
                --service-account="${PROJECT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
                --memory 1Gi \
                --cpu 1 \
                --timeout 120 \
                --max-instances 5
        fi
    done

    log_success "Cloud Run deployment completed"
}

deploy_to_kubernetes() {
    if [ "$KUBERNETES_ENABLED" = false ]; then
        log_warning "Skipping Kubernetes deployment (kubectl not available)"
        return
    fi

    log_info "Deploying to Kubernetes..."

    # Create namespace
    kubectl create namespace ${PROJECT_NAME} --dry-run=client -o yaml | kubectl apply -f -

    # Apply Kubernetes manifests
    if [ -f "k8s/" ]; then
        kubectl apply -f k8s/ -n ${PROJECT_NAME}
    fi

    log_success "Kubernetes deployment completed"
}

setup_monitoring() {
    log_info "Setting up monitoring..."

    # Create monitoring configuration files
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'unified-content-creator'
    static_configs:
      - targets: ['unified-content-creator:8000']
    metrics_path: /metrics

  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'mcp-sequential-thinking:3001'
        - 'mcp-brave-search:3002'
        - 'mcp-memory:3003'
        - 'mcp-filesystem:3004'
        - 'mcp-research-integration:3005'
        - 'mcp-content-validation:3006'
        - 'mcp-advanced-orchestration:3007'
    metrics_path: /metrics
EOF

    # Create Grafana datasource configuration
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log_success "Monitoring setup completed"
}

setup_nginx() {
    log_info "Setting up Nginx configuration..."

    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream unified_backend {
        server unified-content-creator:8000;
    }

    upstream mcp_backend {
        server mcp-sequential-thinking:3001;
        server mcp-brave-search:3002;
        server mcp-memory:3003;
        server mcp-filesystem:3004;
        server mcp-research-integration:3005;
        server mcp-content-validation:3006;
        server mcp-advanced-orchestration:3007;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://unified_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /mcp/ {
            proxy_pass http://mcp_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

    log_success "Nginx configuration created"
}

run_tests() {
    log_info "Running system tests..."

    # Wait for services to be ready
    sleep 30

    # Run basic health checks
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Main system health check passed"
    else
        log_error "Main system health check failed"
        return 1
    fi

    # Run integration tests
    if [ -f "scripts/test_unified_system.py" ]; then
        python scripts/test_unified_system.py
        log_success "Integration tests completed"
    fi

    log_success "System tests completed"
}

show_deployment_info() {
    log_info "Deployment completed successfully!"
    echo
    echo "🌐 Service URLs:"
    echo "  Main System: https://${PROJECT_NAME}-$(gcloud run services describe ${PROJECT_NAME} --region=${REGION} --format='value(status.url)' | sed 's|https://||')"
    echo
    echo "🔧 MCP Servers:"
    for server in sequential-thinking brave-search memory filesystem research-integration content-validation advanced-orchestration; do
        if gcloud run services describe mcp-${server} --region=${REGION} &>/dev/null; then
            echo "  ${server}: https://mcp-${server}-$(gcloud run services describe mcp-${server} --region=${REGION} --format='value(status.url)' | sed 's|https://||')"
        fi
    done
    echo
    echo "📊 Monitoring:"
    echo "  Grafana: http://localhost:3000 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo
    echo "📚 Documentation:"
    echo "  - docs/TOOL_ARCHITECTURE_WORKFLOW.md"
    echo "  - docs/FINAL_IMPLEMENTATION_SUMMARY.md"
    echo "  - README.md"
}

# Main deployment flow
main() {
    echo "🚀 Starting Unified Content Creator System Deployment"
    echo "=================================================="
    echo

    check_prerequisites
    setup_environment
    enable_apis
    setup_service_account
    setup_secrets
    build_and_push_images
    deploy_to_cloud_run
    deploy_to_kubernetes
    setup_monitoring
    setup_nginx
    run_tests
    show_deployment_info

    echo
    log_success "🎉 Deployment completed successfully!"
}

# Run main function
main "$@"
