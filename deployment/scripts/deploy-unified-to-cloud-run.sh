#!/bin/bash

# Enhanced Deployment Script for Unified Content Creator to Google Cloud Run
# This script deploys the complete system including all MCP servers and services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="unified-content-creator"
IMAGE_NAME="unified-content-creator"
SERVICE_ACCOUNT="unified-content-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI (gcloud) is not installed. Please install it first."
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi

    # Check if docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    print_success "Prerequisites check passed!"
}

# Function to set up Google Cloud project
setup_project() {
    print_status "Setting up Google Cloud project..."

    if [ -z "$PROJECT_ID" ]; then
        print_error "PROJECT_ID is not set. Please set it in the script or as an environment variable."
        exit 1
    fi

    # Set the project
    gcloud config set project "$PROJECT_ID" --quiet

    # Enable required APIs
    print_status "Enabling required APIs..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        secretmanager.googleapis.com \
        containerregistry.googleapis.com \
        compute.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com

    print_success "Project setup completed!"
}

# Function to create service account
create_service_account() {
    print_status "Creating service account..."

    # Check if service account already exists
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project "$PROJECT_ID" &> /dev/null; then
        print_warning "Service account already exists, skipping creation."
        return
    fi

    # Create service account
    gcloud iam service-accounts create "unified-content-sa" \
        --display-name="Unified Content Creator Service Account" \
        --description="Service account for Unified Content Creator"

    # Grant necessary roles
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/run.invoker"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/logging.logWriter"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/monitoring.metricWriter"

    print_success "Service account created and configured!"
}

# Function to create secrets
create_secrets() {
    print_status "Creating secrets in Google Secret Manager..."

    # List of required secrets
    declare -a secrets=(
        "UNSPLASH_API_KEY"
        "STABLE_DIFFUSION_API_KEY"
        "PIXABAY_API_KEY"
        "CUSTOM_ICON_API_KEY"
        "BRAVE_API_KEY"
        "POSTGRES_PASSWORD"
        "GRAFANA_PASSWORD"
    )

    for secret in "${secrets[@]}"; do
        if [ -n "${!secret}" ]; then
            print_status "Creating secret: $secret"

            # Check if secret already exists
            if gcloud secrets describe "$secret" --project "$PROJECT_ID" &> /dev/null; then
                print_warning "Secret $secret already exists, updating..."
                echo "${!secret}" | gcloud secrets versions add "$secret" --data-file=- --project "$PROJECT_ID"
            else
                echo "${!secret}" | gcloud secrets create "$secret" --data-file=- --project "$PROJECT_ID"
            fi
        else
            print_warning "Environment variable $secret is not set, skipping..."
        fi
    done

    print_success "Secrets created/updated!"
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."

    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker

    # Build and push main enhanced generator image
    print_status "Building enhanced generator image..."
    docker build -f Dockerfile.enhanced -t "gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" .
    docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"

    # Build and push image generation MCP server
    print_status "Building image generation MCP server..."
    docker build -f Dockerfile.image-generation -t "gcr.io/$PROJECT_ID/mcp-image-generation:latest" .
    docker push "gcr.io/$PROJECT_ID/mcp-image-generation:latest"

    # Build and push icon generation MCP server
    print_status "Building icon generation MCP server..."
    docker build -f Dockerfile.icon-generation -t "gcr.io/$PROJECT_ID/mcp-icon-generation:latest" .
    docker push "gcr.io/$PROJECT_ID/mcp-icon-generation:latest"

    print_success "All Docker images built and pushed!"
}

# Function to deploy to Cloud Run
deploy_to_cloud_run() {
    print_status "Deploying to Google Cloud Run..."

    # Deploy main enhanced generator service
    print_status "Deploying main enhanced generator service..."
    gcloud run deploy "$SERVICE_NAME" \
        --image="gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=8000 \
        --memory="2Gi" \
        --cpu="2" \
        --max-instances=10 \
        --min-instances=1 \
        --timeout=900 \
        --concurrency=80 \
        --set-env-vars="PRESENTON_API_URL=https://presenton-api-${PROJECT_ID}.run.app" \
        --set-env-vars="LOG_LEVEL=INFO" \
        --set-env-vars="ENVIRONMENT=production"

    # Deploy image generation MCP server
    print_status "Deploying image generation MCP server..."
    gcloud run deploy "mcp-image-generation" \
        --image="gcr.io/$PROJECT_ID/mcp-image-generation:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3005 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=5 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=40

    # Deploy icon generation MCP server
    print_status "Deploying icon generation MCP server..."
    gcloud run deploy "mcp-icon-generation" \
        --image="gcr.io/$PROJECT_ID/mcp-icon-generation:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3006 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=5 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=40

    print_success "All services deployed to Cloud Run!"
}

# Function to deploy MCP servers (using Cloud Run jobs for long-running services)
deploy_mcp_servers() {
    print_status "Deploying MCP servers..."

    # Note: For production, you might want to use Cloud Run jobs or GKE for MCP servers
    # For now, we'll use Cloud Run with appropriate configurations

    # Deploy sequential thinking server
    print_status "Deploying sequential thinking MCP server..."
    gcloud run deploy "mcp-sequential-thinking" \
        --image="modelcontextprotocol/server-sequential-thinking:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3001 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=3 \
        --min-instances=1 \
        --timeout=600 \
        --concurrency=20

    # Deploy brave search server
    print_status "Deploying brave search MCP server..."
    gcloud run deploy "mcp-brave-search" \
        --image="modelcontextprotocol/server-brave-search:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3002 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=5 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=30

    # Deploy memory server
    print_status "Deploying memory MCP server..."
    gcloud run deploy "mcp-memory" \
        --image="modelcontextprotocol/server-memory:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3003 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=3 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=20

    # Deploy filesystem server
    print_status "Deploying filesystem MCP server..."
    gcloud run deploy "mcp-filesystem" \
        --image="modelcontextprotocol/server-filesystem:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3004 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=3 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=20

    print_success "All MCP servers deployed!"
}

# Function to deploy Presenton (using Cloud Run)
deploy_presenton() {
    print_status "Deploying Presenton API..."

    # Deploy Presenton service
    gcloud run deploy "presenton-api" \
        --image="presenton/presenton:latest" \
        --platform="managed" \
        --region="$REGION" \
        --service-account="$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --port=3000 \
        --memory="1Gi" \
        --cpu="1" \
        --max-instances=5 \
        --min-instances=1 \
        --timeout=300 \
        --concurrency=30

    print_success "Presenton API deployed!"
}

# Function to set up monitoring and logging
setup_monitoring() {
    print_status "Setting up monitoring and logging..."

    # Create log sink for unified content creator
    gcloud logging sinks create unified-content-sink \
        "storage.googleapis.com/projects/$PROJECT_ID/buckets/unified-content-logs" \
        --log-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\"" \
        --project "$PROJECT_ID"

    # Create custom metrics
    gcloud monitoring custom create \
        --display-name="Content Creation Requests" \
        --type="custom.googleapis.com/content/creation/requests" \
        --description="Number of content creation requests" \
        --project "$PROJECT_ID"

    print_success "Monitoring and logging configured!"
}

# Function to display deployment information
display_deployment_info() {
    print_success "Deployment completed successfully!"
    echo
    echo "🌐 **Service URLs:**"
    echo "   Main Service: https://$SERVICE_NAME-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Image Generation: https://mcp-image-generation-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Icon Generation: https://mcp-icon-generation-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Sequential Thinking: https://mcp-sequential-thinking-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Brave Search: https://mcp-brave-search-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Memory: https://mcp-memory-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Filesystem: https://mcp-filesystem-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo "   Presenton API: https://presenton-api-$(echo $PROJECT_ID | cut -d'-' -f1).run.app"
    echo
    echo "🔧 **Next Steps:**"
    echo "   1. Test the services using the demo scripts"
    echo "   2. Configure custom domains if needed"
    echo "   3. Set up CI/CD pipeline for automated deployments"
    echo "   4. Monitor performance and scale as needed"
    echo
    echo "📚 **Documentation:**"
    echo "   - API docs: https://$SERVICE_NAME-$(echo $PROJECT_ID | cut -d'-' -f1).run.app/docs"
    echo "   - Health checks: https://$SERVICE_NAME-$(echo $PROJECT_ID | cut -d'-' -f1).run.app/health"
}

# Main deployment function
main() {
    echo "🚀 **Unified Content Creator - Google Cloud Run Deployment**"
    echo "=========================================================="
    echo

    # Check prerequisites
    check_prerequisites

    # Setup project
    setup_project

    # Create service account
    create_service_account

    # Create secrets
    create_secrets

    # Build and push images
    build_and_push_images

    # Deploy MCP servers
    deploy_mcp_servers

    # Deploy Presenton
    deploy_presenton

    # Deploy main services
    deploy_to_cloud_run

    # Setup monitoring
    setup_monitoring

    # Display information
    display_deployment_info
}

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID is not set. Please set it in the script or as an environment variable."
    echo "Usage: PROJECT_ID=your-project-id ./deploy-unified-to-cloud-run.sh"
    exit 1
fi

# Run main function
main "$@"
