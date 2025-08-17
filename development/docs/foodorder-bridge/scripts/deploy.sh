#!/bin/bash
# FoodOrder Bridge API Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
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

# Default values
ENVIRONMENT="development"
COMPOSE_FILE="docker-compose.yml"
BUILD_FRESH=false
PULL_IMAGES=false

# Help function
show_help() {
    echo "FoodOrder Bridge API Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENVIRONMENT    Set environment (development/production) [default: development]"
    echo "  -b, --build             Force rebuild images"
    echo "  -p, --pull              Pull latest base images"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Deploy in development mode"
    echo "  $0 -e production        # Deploy in production mode"
    echo "  $0 -e production -b     # Deploy production with fresh build"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_FRESH=true
            shift
            ;;
        -p|--pull)
            PULL_IMAGES=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be 'development' or 'production'"
    exit 1
fi

# Set compose file based on environment
if [[ "$ENVIRONMENT" == "production" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

print_info "Starting deployment for $ENVIRONMENT environment..."

# Check if required files exist
if [[ ! -f ".env" ]]; then
    print_error ".env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Compose file $COMPOSE_FILE not found."
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Pull latest images if requested
if [[ "$PULL_IMAGES" == true ]]; then
    print_info "Pulling latest base images..."
    docker-compose -f "$COMPOSE_FILE" pull
fi

# Build images if requested or if they don't exist
if [[ "$BUILD_FRESH" == true ]]; then
    print_info "Building fresh images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
else
    print_info "Building images (using cache)..."
    docker-compose -f "$COMPOSE_FILE" build
fi

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" down

# Start services
print_info "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check health
print_info "Checking service health..."
max_attempts=30
attempt=1

while [[ $attempt -le $max_attempts ]]; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "API is healthy!"
        break
    else
        if [[ $attempt -eq $max_attempts ]]; then
            print_error "API failed to become healthy after $max_attempts attempts"
            print_info "Checking logs..."
            docker-compose -f "$COMPOSE_FILE" logs foodorder-api
            exit 1
        fi
        print_info "Attempt $attempt/$max_attempts - API not ready yet, waiting..."
        sleep 2
        ((attempt++))
    fi
done

# Show running services
print_info "Running services:"
docker-compose -f "$COMPOSE_FILE" ps

# Show useful URLs
echo ""
print_success "Deployment completed successfully!"
echo ""
print_info "Service URLs:"
if [[ "$ENVIRONMENT" == "development" ]]; then
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  API Health Check:  http://localhost:8000/health"
    echo "  Redis (optional):  redis://localhost:6379"
else
    echo "  API Documentation: https://your-domain.com/docs"
    echo "  API Health Check:  https://your-domain.com/health"
    echo "  Monitoring:        http://localhost:9090 (Prometheus)"
    echo "  Grafana:           http://localhost:3000 (admin/admin123)"
fi

echo ""
print_info "Useful commands:"
echo "  View logs:         docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop services:     docker-compose -f $COMPOSE_FILE down"
echo "  Update cache:      curl -X POST http://localhost:8000/api/v1/cache/reload"
echo ""