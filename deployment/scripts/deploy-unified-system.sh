#!/bin/bash

# Unified Content Creator System - Complete Deployment Script
# This script deploys the entire unified content creation system to Google Cloud Run

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
SERVICE_ACCOUNT_NAME="unified-content-creator-sa"
SERVICE_ACCOUNT_EMAIL=""
IMAGE_TAG="latest"
DOCKER_REGISTRY="gcr.io"

# Service configurations
SERVICES=(
    "unified-main:8000:src/mcp_server_openai"
    "image-generation:3005:src/mcp_server_openai/tools/enhanced_image_generator.py"
    "icon-generation:3006:src/mcp_server_openai/tools/enhanced_icon_generator.py"
    "document-generation:3007:src/mcp_server_openai/tools/enhanced_document_generator.py"
)

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
            print_error "PROJECT_ID is not set. Please set it in the script or run 'gcloud config set project YOUR_PROJECT_ID'"
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

    APIs=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "iam.googleapis.com"
        "containerregistry.googleapis.com"
    )

    for api in "${APIs[@]}"; do
        if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            print_status "API $api is already enabled"
        else
            print_status "Enabling API: $api"
            gcloud services enable "$api" --project="$PROJECT_ID"
        fi
    done

    print_success "All required APIs enabled"
}

# Function to create service account
create_service_account() {
    print_status "Creating service account..."

    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
        print_status "Service account already exists"
    else
        gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
            --display-name="Unified Content Creator Service Account" \
            --description="Service account for Unified Content Creator system" \
            --project="$PROJECT_ID"

        SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    fi

    # Grant necessary roles
    print_status "Granting necessary roles to service account..."

    ROLES=(
        "roles/run.admin"
        "roles/iam.serviceAccountUser"
        "roles/secretmanager.secretAccessor"
        "roles/storage.admin"
        "roles/logging.logWriter"
        "roles/monitoring.metricWriter"
    )

    for role in "${ROLES[@]}"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
            --role="$role"
    done

    print_success "Service account created and configured"
}

# Function to set up secrets
setup_secrets() {
    print_status "Setting up secrets in Google Secret Manager..."

    SECRETS=(
        "OPENAI_API_KEY"
        "ANTHROPIC_API_KEY"
        "GOOGLE_API_KEY"
        "UNSPLASH_API_KEY"
        "STABLE_DIFFUSION_API_KEY"
        "PIXABAY_API_KEY"
        "ICONIFY_API_KEY"
        "LUCIDE_API_KEY"
        "PRESENTON_API_KEY"
    )

    for secret in "${SECRETS[@]}"; do
        if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
            print_status "Secret $secret already exists"
        else
            print_warning "Secret $secret does not exist. Please create it manually:"
            echo "gcloud secrets create $secret --project=$PROJECT_ID"
            echo "echo 'YOUR_API_KEY' | gcloud secrets versions add $secret --data-file=- --project=$PROJECT_ID"
        fi
    done

    print_success "Secrets setup completed"
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."

    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port dockerfile_path <<< "$service_config"

        print_status "Building image for $service_name..."

        # Build the image
        docker build \
            -f "Dockerfile.$service_name" \
            -t "$DOCKER_REGISTRY/$PROJECT_ID/$service_name:$IMAGE_TAG" \
            .

        # Push to Google Container Registry
        print_status "Pushing image for $service_name..."
        docker push "$DOCKER_REGISTRY/$PROJECT_ID/$service_name:$IMAGE_TAG"

        print_success "Image for $service_name built and pushed"
    done

    print_success "All Docker images built and pushed"
}

# Function to deploy to Cloud Run
deploy_to_cloud_run() {
    print_status "Deploying services to Google Cloud Run..."

    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port dockerfile_path <<< "$service_config"

        print_status "Deploying $service_name..."

        # Deploy the service
        gcloud run deploy "$service_name" \
            --image="$DOCKER_REGISTRY/$PROJECT_ID/$service_name:$IMAGE_TAG" \
            --platform="managed" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --service-account="$SERVICE_ACCOUNT_EMAIL" \
            --port="$port" \
            --memory="2Gi" \
            --cpu="2" \
            --max-instances="10" \
            --min-instances="0" \
            --concurrency="80" \
            --timeout="900" \
            --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
            --allow-unauthenticated \
            --set-cloudsql-instances="" \
            --add-cloudsql-instances="" \
            --update-env-vars=""

        print_success "$service_name deployed successfully"
    done

    print_success "All services deployed to Cloud Run"
}

# Function to configure secrets for services
configure_service_secrets() {
    print_status "Configuring secrets for services..."

    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port dockerfile_path <<< "$service_config"

        print_status "Configuring secrets for $service_name..."

        # Update the service with secrets
        gcloud run services update "$service_name" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --update-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest" \
            --update-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest" \
            --update-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
            --update-secrets="UNSPLASH_API_KEY=UNSPLASH_API_KEY:latest" \
            --update-secrets="STABLE_DIFFUSION_API_KEY=STABLE_DIFFUSION_API_KEY:latest" \
            --update-secrets="PIXABAY_API_KEY=PIXABAY_API_KEY:latest" \
            --update-secrets="ICONIFY_API_KEY=ICONIFY_API_KEY:latest" \
            --update-secrets="LUCIDE_API_KEY=LUCIDE_API_KEY:latest" \
            --update-secrets="PRESENTON_API_KEY=PRESENTON_API_KEY:latest"

        print_success "Secrets configured for $service_name"
    done

    print_success "All service secrets configured"
}

# Function to set up monitoring and logging
setup_monitoring() {
    print_status "Setting up monitoring and logging..."

    # Create log sink
    if ! gcloud logging sinks describe "unified-content-logs" --project="$PROJECT_ID" &>/dev/null; then
        gcloud logging sinks create "unified-content-logs" \
            "storage.googleapis.com/$PROJECT_ID-unified-content-logs" \
            --project="$PROJECT_ID" \
            --log-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=~\"unified-.*\""
    fi

    # Create alerting policy
    if ! gcloud alpha monitoring policies list --filter="displayName:Unified Content Creator Alerts" --project="$PROJECT_ID" --format="value(name)" | grep -q "policies"; then
        print_status "Creating alerting policy..."
        # This would create a comprehensive alerting policy
        # For brevity, we'll skip the detailed policy creation
        print_warning "Please create alerting policies manually in the Google Cloud Console"
    fi

    print_success "Monitoring and logging setup completed"
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."

    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port dockerfile_path <<< "$service_config"

        # Get the service URL
        SERVICE_URL=$(gcloud run services describe "$service_name" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --format="value(status.url)")

        if [ -n "$SERVICE_URL" ]; then
            print_status "Checking health of $service_name at $SERVICE_URL"

            # Try to access the health endpoint
            if curl -f -s "$SERVICE_URL/health" > /dev/null; then
                print_success "$service_name is healthy"
            else
                print_warning "$service_name health check failed"
            fi
        else
            print_warning "Could not get URL for $service_name"
        fi
    done

    print_success "Health checks completed"
}

# Function to display deployment summary
show_deployment_summary() {
    print_success "🎉 Unified Content Creator System Deployment Complete!"
    echo
    echo "📋 Deployment Summary:"
    echo "========================"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
    echo

    echo "🚀 Deployed Services:"
    echo "======================"
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port dockerfile_path <<< "$service_config"
        SERVICE_URL=$(gcloud run services describe "$service_name" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --format="value(status.url)" 2>/dev/null || echo "N/A")
        echo "  • $service_name: $SERVICE_URL"
    done
    echo

    echo "🔑 API Endpoints:"
    echo "================="
    MAIN_SERVICE_URL=$(gcloud run services describe "unified-main" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)" 2>/dev/null || echo "N/A")

    if [ "$MAIN_SERVICE_URL" != "N/A" ]; then
        echo "  • Unified Content Creation: $MAIN_SERVICE_URL/api/v1/unified/create"
        echo "  • Supported Formats: $MAIN_SERVICE_URL/api/v1/unified/formats"
        echo "  • Content Status: $MAIN_SERVICE_URL/api/v1/unified/status/{client_id}"
        echo "  • PPT Generation: $MAIN_SERVICE_URL/api/v1/ppt/generate"
        echo "  • Document Generation: $MAIN_SERVICE_URL/api/v1/document/generate"
    fi
    echo

    echo "📚 Next Steps:"
    echo "==============="
    echo "1. Test the API endpoints using the demo scripts"
    echo "2. Monitor the services in Google Cloud Console"
    echo "3. Set up custom domain names if needed"
    echo "4. Configure additional monitoring and alerting"
    echo "5. Set up CI/CD pipelines for future updates"
    echo

    echo "🔧 Useful Commands:"
    echo "==================="
    echo "  • View logs: gcloud logging read 'resource.type=\"cloud_run_revision\"' --limit=50"
    echo "  • Scale service: gcloud run services update SERVICE_NAME --max-instances=20"
    echo "  • Update image: gcloud run services update SERVICE_NAME --image=IMAGE_URL"
    echo "  • Delete service: gcloud run services delete SERVICE_NAME --region=$REGION"
    echo

    echo "📖 Documentation:"
    echo "================="
    echo "  • README.md - Main project documentation"
    echo "  • DEPLOYMENT_STATUS.md - Current deployment status"
    echo "  • scripts/demo_*.py - Demo and testing scripts"
    echo "  • config/unified_system.yaml - System configuration"
}

# Main deployment function
main() {
    echo "🚀 Unified Content Creator System - Complete Deployment"
    echo "======================================================"
    echo

    # Check prerequisites
    check_prerequisites

    # Enable APIs
    enable_apis

    # Create service account
    create_service_account

    # Set up secrets
    setup_secrets

    # Build and push images
    build_and_push_images

    # Deploy to Cloud Run
    deploy_to_cloud_run

    # Configure secrets for services
    configure_service_secrets

    # Set up monitoring
    setup_monitoring

    # Wait a bit for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30

    # Run health checks
    run_health_checks

    # Show deployment summary
    show_deployment_summary
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --service-account)
                SERVICE_ACCOUNT_NAME="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --project-id PROJECT_ID     Google Cloud Project ID"
                echo "  --region REGION            Google Cloud region (default: us-central1)"
                echo "  --service-account NAME     Service account name (default: unified-content-creator-sa)"
                echo "  --image-tag TAG            Docker image tag (default: latest)"
                echo "  --help                     Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Run main deployment
    main
fi
