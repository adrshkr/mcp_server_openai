#!/bin/bash
set -euo pipefail

# Optimized deployment script for GCP Cloud Run
# Includes security best practices, performance optimization, and cost control

# Configuration
PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="mcp-server-openai"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Resolve important paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUD_RUN_YAML="${SCRIPT_DIR}/../cloud-run/cloud-run-service.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if [ -z "$PROJECT_ID" ]; then
        log_error "PROJECT_ID environment variable must be set"
        exit 1
    fi

    # Check if gcloud is installed and authenticated
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi

    # Ensure gcloud uses the provided project by default
    gcloud config set project "$PROJECT_ID" --quiet >/dev/null

    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build optimized Docker image
build_image() {
    log_info "Building optimized Docker image..."

    # Enable BuildKit for better caching
    export DOCKER_BUILDKIT=1

    # Build multi-stage image with caching
    docker build \
        --tag "${IMAGE_NAME}:latest" \
        --tag "${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S)" \
        --cache-from "${IMAGE_NAME}:latest" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .

    log_info "Docker image built successfully"
}

# Push image to Container Registry
push_image() {
    log_info "Pushing image to Google Container Registry..."

    # Configure Docker to use gcloud as credential helper
    gcloud auth configure-docker --quiet

    # Push image
    docker push "${IMAGE_NAME}:latest"

    log_info "Image pushed successfully"
}

# Create secrets in Secret Manager if they don't exist
create_secrets() {
    log_info "Setting up GCP Secret Manager secrets..."

    secrets=(
        "openai-api-key"
        "anthropic-api-key"
        "google-api-key"
        "unsplash-access-key"
        "unsplash-secret-key"
        "pixabay-api-key"
    )

    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe "$secret" --project="$PROJECT_ID" --quiet &>/dev/null; then
            log_warn "Secret $secret does not exist. Creating placeholder..."
            echo "REPLACE_WITH_ACTUAL_KEY" | gcloud secrets create "$secret" --project="$PROJECT_ID" --data-file=-
            log_warn "Please update secret $secret with actual value using:"
            log_warn "  echo 'your-actual-key' | gcloud secrets versions add $secret --project=$PROJECT_ID --data-file=-"
        else
            log_info "Secret $secret already exists"
        fi
    done
}

# Create service account with minimal permissions
create_service_account() {
    local sa_name="mcp-server-sa"
    local sa_email="${sa_name}@${PROJECT_ID}.iam.gserviceaccount.com"

    log_info "Setting up service account..."

    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe "$sa_email" --project="$PROJECT_ID" --quiet &>/dev/null; then
        gcloud iam service-accounts create "$sa_name" \
            --project="$PROJECT_ID" \
            --display-name="MCP Server OpenAI Service Account" \
            --description="Service account for MCP Server with minimal permissions"
    fi

    # Grant minimal required permissions
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$sa_email" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet

    log_info "Service account configured"
}

# Deploy to Cloud Run with optimized configuration
deploy_service() {
    log_info "Deploying to Cloud Run with optimized configuration..."

    # Deploy using the optimized cloud-run-service.yaml
    sed "s/PROJECT_ID/${PROJECT_ID}/g" "$CLOUD_RUN_YAML" | \
    gcloud run services replace - \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --quiet

    log_info "Service deployed successfully"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)")

    log_info "Service URL: $SERVICE_URL"

    # Test health endpoints
    log_info "Testing health endpoints..."
    sleep 10  # Wait for service to be ready

    if curl -f "$SERVICE_URL/health/live" &>/dev/null; then
        log_info "✅ Liveness probe: OK"
    else
        log_warn "❌ Liveness probe: FAILED"
    fi

    if curl -f "$SERVICE_URL/health/ready" &>/dev/null; then
        log_info "✅ Readiness probe: OK"
    else
        log_warn "❌ Readiness probe: FAILED"
    fi

    log_info "Deployment completed!"
    log_info "Health status: $SERVICE_URL/status"
    log_info "Service info: $SERVICE_URL/info"
}

# Main deployment function
main() {
    log_info "Starting optimized deployment to GCP Cloud Run..."
    log_info "Project ID: $PROJECT_ID"
    log_info "Region: $REGION"
    log_info "Service Name: $SERVICE_NAME"

    check_prerequisites
    create_secrets
    create_service_account
    build_image
    push_image
    deploy_service

    log_info "🎉 Deployment completed successfully!"
    log_info "Your MCP Server OpenAI is now running on Cloud Run with:"
    log_info "  - Comprehensive health monitoring"
    log_info "  - Security hardening (non-root, Secret Manager)"
    log_info "  - Performance optimization (uvloop, startup validation)"
    log_info "  - Cost optimization (auto-scaling, resource limits)"
}

# Run main function
main "$@"
