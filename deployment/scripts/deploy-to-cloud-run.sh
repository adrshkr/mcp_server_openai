#!/bin/bash

# Enhanced PPT Generator - Google Cloud Run Deployment Script
# This script automates the deployment process to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-your-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="enhanced-ppt-generator"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
DOCKERFILE="Dockerfile.enhanced"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "You are not authenticated with gcloud. Please run 'gcloud auth login' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to set up Google Cloud project
setup_project() {
    print_status "Setting up Google Cloud project..."
    
    # Set the project
    gcloud config set project "${PROJECT_ID}"
    
    # Enable required APIs
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    print_success "Project setup completed"
}

# Function to build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Build the image
    print_status "Building Docker image..."
    docker build -f "${DOCKERFILE}" -t "${IMAGE_NAME}" .
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker
    
    # Push the image
    print_status "Pushing Docker image to Google Container Registry..."
    docker push "${IMAGE_NAME}"
    
    print_success "Docker image built and pushed successfully"
}

# Function to deploy to Cloud Run
deploy_to_cloud_run() {
    print_status "Deploying to Google Cloud Run..."
    
    # Deploy the service
    gcloud run deploy "${SERVICE_NAME}" \
        --image "${IMAGE_NAME}" \
        --platform managed \
        --region "${REGION}" \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2 \
        --timeout 300 \
        --concurrency 80 \
        --max-instances 10 \
        --set-env-vars PRESENTON_API_URL="${PRESENTON_API_URL:-http://localhost:5000}" \
        --set-env-vars MCP_MONITORING_ENABLED=true \
        --set-env-vars MCP_COST_HOURLY_MAX=50.0 \
        --set-env-vars MCP_COST_DAILY_MAX=500.0
    
    print_success "Deployment to Cloud Run completed"
}

# Function to set up secrets
setup_secrets() {
    print_status "Setting up API key secrets..."
    
    # Check if secrets exist
    if ! gcloud secrets list --filter="name:openai-api-key" --format="value(name)" | grep -q .; then
        print_warning "OpenAI API key secret not found. Creating..."
        echo "${OPENAI_API_KEY}" | gcloud secrets create openai-api-key --data-file=-
    fi
    
    if ! gcloud secrets list --filter="name:anthropic-api-key" --format="value(name)" | grep -q .; then
        print_warning "Anthropic API key secret not found. Creating..."
        echo "${ANTHROPIC_API_KEY}" | gcloud secrets create anthropic-api-key --data-file=-
    fi
    
    if ! gcloud secrets list --filter="name:google-api-key" --format="value(name)" | grep -q .; then
        print_warning "Google API key secret not found. Creating..."
        echo "${GOOGLE_API_KEY}" | gcloud secrets create google-api-key --data-file=-
    fi
    
    print_success "API key secrets setup completed"
}

# Function to update service with secrets
update_service_with_secrets() {
    print_status "Updating service with API key secrets..."
    
    gcloud run services update "${SERVICE_NAME}" \
        --region "${REGION}" \
        --update-secrets OPENAI_API_KEY=openai-api-key:latest \
        --update-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest \
        --update-secrets GOOGLE_API_KEY=google-api-key:latest
    
    print_success "Service updated with secrets"
}

# Function to show deployment information
show_deployment_info() {
    print_status "Getting deployment information..."
    
    SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)")
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "Service Information:"
    echo "  Name: ${SERVICE_NAME}"
    echo "  URL: ${SERVICE_URL}"
    echo "  Region: ${REGION}"
    echo "  Project: ${PROJECT_ID}"
    echo ""
    echo "API Endpoints:"
    echo "  Health Check: ${SERVICE_URL}/health"
    echo "  PPT Generation: ${SERVICE_URL}/api/v1/ppt/generate"
    echo "  Content Analysis: ${SERVICE_URL}/api/v1/ppt/analyze"
    echo "  Templates: ${SERVICE_URL}/api/v1/ppt/templates"
    echo ""
    echo "To test the service:"
    echo "  curl ${SERVICE_URL}/health"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 Enhanced PPT Generator - Google Cloud Run Deployment"
    echo "======================================================"
    echo ""
    
    # Check if PROJECT_ID is set
    if [ "${PROJECT_ID}" = "your-project-id" ]; then
        print_error "Please set PROJECT_ID environment variable or update the script"
        echo "Usage: PROJECT_ID=your-actual-project-id ./deploy-to-cloud-run.sh"
        exit 1
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Setup project
    setup_project
    
    # Setup secrets (if API keys are provided)
    if [ -n "${OPENAI_API_KEY}" ] || [ -n "${ANTHROPIC_API_KEY}" ] || [ -n "${GOOGLE_API_KEY}" ]; then
        setup_secrets
    else
        print_warning "API keys not provided. Skipping secrets setup."
        print_warning "You can set them later using:"
        echo "  gcloud secrets create openai-api-key --data-file=-"
        echo "  gcloud secrets create anthropic-api-key --data-file=-"
        echo "  gcloud secrets create google-api-key --data-file=-"
    fi
    
    # Build and push image
    build_and_push_image
    
    # Deploy to Cloud Run
    deploy_to_cloud_run
    
    # Update service with secrets if they exist
    if gcloud secrets list --filter="name:openai-api-key" --format="value(name)" | grep -q .; then
        update_service_with_secrets
    fi
    
    # Show deployment information
    show_deployment_info
}

# Run main function
main "$@"

