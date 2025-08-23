#!/bin/bash

# Enhanced Document Generation Service Deployment Script
# This script deploys the enhanced document generation service to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="enhanced-document-generation"
IMAGE_NAME="enhanced-document-generation"
SERVICE_ACCOUNT="document-generation-sa@${PROJECT_ID}.iam.gserviceaccount.com"

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

    # Check if PROJECT_ID is set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "PROJECT_ID is not set. Please set it in the script or run 'gcloud config set project PROJECT_ID'"
            exit 1
        fi
        print_status "Using project: $PROJECT_ID"
    fi

    # Ensure gcloud uses the provided project by default
    gcloud config set project "$PROJECT_ID" --quiet >/dev/null

    print_success "Prerequisites check passed"
}

# Function to enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."

    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        secretmanager.googleapis.com \
        containerregistry.googleapis.com \
        --project="$PROJECT_ID"

    print_success "APIs enabled successfully"
}

# Function to create service account
create_service_account() {
    print_status "Creating service account for document generation service..."

    # Check if service account already exists
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" &>/dev/null; then
        print_warning "Service account already exists, skipping creation"
        return
    fi

    gcloud iam service-accounts create "document-generation-sa" \
        --display-name="Document Generation Service Account" \
        --description="Service account for enhanced document generation service" \
        --project="$PROJECT_ID"

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

    print_success "Service account created and configured"
}

# Function to build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."

    # Build the image
    docker build -f Dockerfile.document-generation -t "gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" .

    # Configure docker to use gcloud as a credential helper
    gcloud auth configure-docker --quiet

    # Push the image
    docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"

    print_success "Docker image built and pushed successfully"
}

# Function to create secrets
create_secrets() {
    print_status "Creating secrets for document generation service..."

    # Create external API key secret (if needed)
    echo "Please enter the external API key for document generation services (or press Enter to skip):"
    read -r EXTERNAL_API_KEY

    if [ -n "$EXTERNAL_API_KEY" ]; then
        echo "$EXTERNAL_API_KEY" | gcloud secrets create "document-generation-external-api-key" \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        print_success "External API key secret created"
    fi

    # Create custom font API key secret (if needed)
    echo "Please enter the custom font API key (or press Enter to skip):"
    read -r CUSTOM_FONT_API_KEY

    if [ -n "$CUSTOM_FONT_API_KEY" ]; then
        echo "$CUSTOM_FONT_API_KEY" | gcloud secrets create "document-generation-font-api-key" \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        print_success "Custom font API key secret created"
    fi
}

# Function to deploy to Cloud Run
deploy_to_cloud_run() {
    print_status "Deploying document generation service to Cloud Run..."

    # Update the Cloud Run YAML with the correct project ID
    sed "s/PROJECT_ID/$PROJECT_ID/g" cloudrun-document-generation.yaml > cloudrun-document-generation-deploy.yaml

    # Deploy using kubectl (requires gcloud auth)
    gcloud container clusters get-credentials "$(gcloud container clusters list --project="$PROJECT_ID" --limit=1 --format="value(name)")" \
        --region="$REGION" \
        --project="$PROJECT_ID" || {
        print_warning "No GKE cluster found, deploying directly to Cloud Run..."

        # Deploy directly to Cloud Run
        gcloud run deploy "$SERVICE_NAME" \
            --image="gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --platform="managed" \
            --allow-unauthenticated \
            --memory="4Gi" \
            --cpu="2" \
            --timeout="300" \
            --concurrency="10" \
            --port="3007" \
            --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,MAX_WORKERS=4,TEMPLATE_CACHE_SIZE=100,PANDOC_TIMEOUT=60,WEASYPRINT_TIMEOUT=30,REPORTLAB_TIMEOUT=30" \
            --service-account="$SERVICE_ACCOUNT"

        return
    }

    # Deploy using kubectl
    kubectl apply -f cloudrun-document-generation-deploy.yaml

    # Wait for deployment to be ready
    kubectl wait --for=condition=ready pod -l serving.knative.dev/service="$SERVICE_NAME" --timeout=300s

    print_success "Document generation service deployed successfully"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)")

    if [ -z "$SERVICE_URL" ]; then
        print_error "Could not get service URL"
        return 1
    fi

    print_success "Service URL: $SERVICE_URL"

    # Test the health endpoint
    print_status "Testing health endpoint..."
    if curl -f "$SERVICE_URL/health" &>/dev/null; then
        print_success "Health check passed"
    else
        print_warning "Health check failed (service might still be starting)"
    fi

    # Test document generation endpoint
    print_status "Testing document generation endpoint..."
    if curl -f "$SERVICE_URL/api/v1/documents/templates" &>/dev/null; then
        print_success "Document generation endpoint is working"
    else
        print_warning "Document generation endpoint test failed (service might still be starting)"
    fi
}

# Function to display deployment information
display_deployment_info() {
    print_success "Enhanced Document Generation Service deployment completed!"
    echo
    echo "Service Information:"
    echo "  - Service Name: $SERVICE_NAME"
    echo "  - Project ID: $PROJECT_ID"
    echo "  - Region: $REGION"
    echo "  - Service Account: $SERVICE_ACCOUNT"
    echo
    echo "Available Endpoints:"
    echo "  - Health Check: /health"
    echo "  - Document Generation: /api/v1/documents/generate"
    echo "  - Templates: /api/v1/documents/templates"
    echo "  - Formats: /api/v1/documents/formats"
    echo
    echo "Supported Formats:"
    echo "  - DOCX (Microsoft Word)"
    echo "  - PDF (Portable Document Format)"
    echo "  - HTML (Web documents with Tailwind CSS)"
    echo "  - Markdown"
    echo "  - LaTeX"
    echo "  - RTF (Rich Text Format)"
    echo
    echo "Templates Available:"
    echo "  - Professional (business-ready)"
    echo "  - Academic (formal documents)"
    echo "  - Creative (visually appealing)"
    echo "  - Minimalist (clean, focused)"
    echo "  - Corporate (branded documents)"
    echo
    echo "Next Steps:"
    echo "  1. Test the service endpoints"
    echo "  2. Configure monitoring and logging"
    echo "  3. Set up custom templates if needed"
    echo "  4. Configure external API keys if required"
}

# Main deployment function
main() {
    echo "🚀 Enhanced Document Generation Service Deployment"
    echo "=================================================="
    echo

    check_prerequisites
    enable_apis
    create_service_account
    create_secrets
    build_and_push_image
    deploy_to_cloud_run
    verify_deployment
    display_deployment_info

    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
