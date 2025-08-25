#!/bin/bash
# Comprehensive Testing Script for MCP Server OpenAI Tools
# Tests both local Docker deployment and Google Cloud Run deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to test API endpoint
test_api_endpoint() {
    local url=$1
    local endpoint=$2
    local description=$3

    print_status "Testing $description at $url$endpoint"

    response=$(curl -s -w "%{http_code}" -o /tmp/api_response "$url$endpoint" || echo "000")

    if [ "$response" = "200" ] || [ "$response" = "404" ] || [ "$response" = "405" ]; then
        print_success "$description: Available (HTTP $response)"
        return 0
    else
        print_error "$description: Failed (HTTP $response)"
        return 1
    fi
}

# Function to test environment setup
test_environment() {
    print_status "Testing Environment Configuration"
    echo "=================================="

    # Check if .env file exists
    if [ -f .env ]; then
        print_success ".env file found"

        # Load environment variables
        export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)

        # Check required API keys
        if [ -n "$OPENAI_API_KEY" ]; then
            print_success "OPENAI_API_KEY: Configured (${OPENAI_API_KEY:0:10}...)"
        else
            print_warning "OPENAI_API_KEY: Not configured"
        fi

        if [ -n "$ANTHROPIC_API_KEY" ]; then
            print_success "ANTHROPIC_API_KEY: Configured (${ANTHROPIC_API_KEY:0:10}...)"
        else
            print_warning "ANTHROPIC_API_KEY: Not configured"
        fi

        if [ -n "$GOOGLE_API_KEY" ]; then
            print_success "GOOGLE_API_KEY: Configured (${GOOGLE_API_KEY:0:10}...)"
        else
            print_warning "GOOGLE_API_KEY: Not configured"
        fi

        if [ -n "$PROJECT_ID" ]; then
            print_success "PROJECT_ID: $PROJECT_ID"
        else
            print_warning "PROJECT_ID: Not configured"
        fi

        if [ -n "$REGION" ]; then
            print_success "REGION: $REGION"
        else
            print_warning "REGION: Not configured"
        fi
    else
        print_error ".env file not found"
        return 1
    fi
}

# Function to test local Docker deployment
test_local_docker() {
    print_status "Testing Local Docker Deployment"
    echo "==============================="

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        return 1
    fi

    print_success "Docker is running"

    # Build and start services
    print_status "Building and starting services..."
    docker-compose -f docker-compose.local.yml up -d --build

    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30

    # Test main API
    if test_api_endpoint "http://localhost:8000" "/health" "Main API Health"; then
        print_success "Main API is running"
    else
        print_error "Main API failed"
    fi

    # Test Presenton API
    if test_api_endpoint "http://localhost:5000" "/api/v1/ppt/presentation/generate" "Presenton API"; then
        print_success "Presenton API is running"
    else
        print_error "Presenton API failed"
    fi

    # Show container status
    print_status "Container Status:"
    docker-compose -f docker-compose.local.yml ps

    # Show logs if there are issues
    print_status "Recent logs:"
    docker-compose -f docker-compose.local.yml logs --tail=10
}

# Function to test Google Cloud deployment
test_gcp_deployment() {
    print_status "Testing Google Cloud Deployment"
    echo "==============================="

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI (gcloud) is not installed"
        return 1
    fi

    print_success "Google Cloud CLI is available"

    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        return 1
    fi

    print_success "Google Cloud authentication verified"

    # Run deployment script
    print_status "Running deployment script..."
    chmod +x deployment/scripts/deploy-unified-to-cloud-run.sh
    ./deployment/scripts/deploy-unified-to-cloud-run.sh

    # Test deployed service
    if [ -n "$PROJECT_ID" ] && [ -n "$REGION" ]; then
        SERVICE_URL="https://unified-content-creator-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]')-$(echo $REGION | tr '_' '-')-RANDOM.a.run.app"
        print_status "Service should be available at: $SERVICE_URL"
        print_status "Note: Exact URL will be shown after deployment completes"
    fi
}

# Function to test specific tools
test_tools() {
    local base_url=$1

    print_status "Testing Tool Endpoints"
    echo "======================"

    # Test content generation
    print_status "Testing content generation tool..."
    curl -X POST "$base_url/api/v1/content/create" \
        -H "Content-Type: application/json" \
        -d '{
            "brief": "Create a test presentation about AI",
            "content_type": "presentation",
            "target_length": "5 slides"
        }' \
        -w "\nHTTP Status: %{http_code}\n" || true

    # Test document generation
    print_status "Testing document generation tool..."
    curl -X POST "$base_url/api/v1/document/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Test Document",
            "content": "# Test Document\n\nThis is a test document about machine learning.",
            "output_format": "markdown",
            "template": "professional"
        }' \
        -w "\nHTTP Status: %{http_code}\n" || true

    # Test image generation
    print_status "Testing image generation tool..."
    curl -X POST "$base_url/api/v1/image/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "query": "A simple diagram showing AI concepts",
            "style": "professional",
            "format": "jpeg",
            "count": 1
        }' \
        -w "\nHTTP Status: %{http_code}\n" || true
}

# Function to cleanup local deployment
cleanup_local() {
    print_status "Cleaning up local deployment..."
    docker-compose -f docker-compose.local.yml down -v
    print_success "Local deployment cleaned up"
}

# Main function
main() {
    echo "🧪 MCP Server OpenAI - Comprehensive Testing Suite"
    echo "=================================================="

    # Test environment
    if ! test_environment; then
        print_error "Environment test failed. Please fix configuration."
        exit 1
    fi

    # Choose deployment type
    echo ""
    echo "Choose deployment type to test:"
    echo "1. Local Docker deployment (recommended for testing)"
    echo "2. Google Cloud Run deployment"
    echo "3. Both (local first, then GCP)"
    echo "4. Tool testing only (requires running service)"
    echo "5. Cleanup local deployment"

    read -p "Enter your choice (1-5): " choice

    case $choice in
        1)
            test_local_docker
            echo ""
            echo "🧪 Tool Testing (Local)"
            test_tools "http://localhost:8000"
            ;;
        2)
            test_gcp_deployment
            ;;
        3)
            test_local_docker
            echo ""
            read -p "Press Enter to continue with GCP deployment..."
            test_gcp_deployment
            ;;
        4)
            read -p "Enter base URL (e.g., http://localhost:8000): " base_url
            test_tools "$base_url"
            ;;
        5)
            cleanup_local
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac

    print_success "Testing completed!"

    echo ""
    echo "📋 Next Steps:"
    echo "============="
    echo "1. If local testing works, you can access:"
    echo "   - Main API: http://localhost:8000"
    echo "   - Presenton: http://localhost:5000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "2. Test individual tools using the curl commands shown above"
    echo ""
    echo "3. For production deployment, use the Google Cloud option"
    echo ""
    echo "4. Check logs with: docker-compose -f docker-compose.local.yml logs"
}

# Run main function
main "$@"
