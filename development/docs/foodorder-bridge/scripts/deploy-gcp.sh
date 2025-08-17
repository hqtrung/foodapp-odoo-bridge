#!/bin/bash
# Cloud Run Deployment Script for FoodOrder Bridge API
# Deploys to Southeast Asia (Singapore) with custom domain and HTTPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
PROJECT_ID="finiziapp"
SERVICE_NAME="foodorder-bridge"
REGION="asia-southeast1"  # Singapore
DOMAIN="api.patedeli.com"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Default values
BUILD_ONLY=false
DEPLOY_ONLY=false
SETUP_DOMAIN=false

# Help function
show_help() {
    echo "Cloud Run Deployment Script for FoodOrder Bridge API"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --build-only     Only build and push image"
    echo "  -d, --deploy-only    Only deploy (skip build)"
    echo "  -s, --setup-domain   Setup custom domain and SSL"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Full deployment (build + deploy)"
    echo "  $0 --build-only      # Only build and push image"
    echo "  $0 --deploy-only     # Deploy existing image"
    echo "  $0 --setup-domain    # Setup api.patedeli.com domain"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -d|--deploy-only)
            DEPLOY_ONLY=true
            shift
            ;;
        -s|--setup-domain)
            SETUP_DOMAIN=true
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

# Check if gcloud is authenticated
print_info "Checking GCP authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "No active GCP authentication found. Run 'gcloud auth login'"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
print_success "Authenticated as: $ACTIVE_ACCOUNT"

# Set project
print_info "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    print_error ".env file not found. Please create it with your Odoo credentials."
    exit 1
fi

# Load environment variables safely
print_info "Loading environment variables..."
set -a  # automatically export all variables
source .env
set +a  # stop auto-export

# Validate required environment variables
if [[ -z "$ODOO_URL" || -z "$ODOO_DB" || -z "$ODOO_USERNAME" || -z "$ODOO_API_KEY" ]]; then
    print_error "Missing required environment variables in .env file"
    print_error "Required: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY"
    exit 1
fi

# Build and push image
if [[ "$DEPLOY_ONLY" != true ]]; then
    print_info "Building and pushing Docker image..."
    
    # Enable required APIs
    print_info "Enabling required GCP APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable firestore.googleapis.com
    
    # Build with Cloud Build
    print_info "Building image with Cloud Build..."
    gcloud builds submit --tag $IMAGE_NAME --timeout=20m
    
    print_success "Image built and pushed: $IMAGE_NAME"
    
    if [[ "$BUILD_ONLY" == true ]]; then
        print_success "Build completed! Use --deploy-only to deploy."
        exit 0
    fi
fi

# Deploy to Cloud Run
if [[ "$BUILD_ONLY" != true ]]; then
    print_info "Deploying to Cloud Run in $REGION..."
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --concurrency 80 \
        --max-instances 3 \
        --min-instances 0 \
        --set-env-vars "ODOO_URL=$ODOO_URL,ODOO_DB=$ODOO_DB,ODOO_USERNAME=$ODOO_USERNAME,ODOO_API_KEY=$ODOO_API_KEY,ENVIRONMENT=production,DEBUG=false" \
        --port 8000
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")
    print_success "Service deployed successfully!"
    print_info "Service URL: $SERVICE_URL"
fi

# Setup custom domain
if [[ "$SETUP_DOMAIN" == true ]]; then
    print_info "Setting up custom domain: $DOMAIN"
    
    # Create domain mapping
    print_info "Creating domain mapping..."
    gcloud beta run domain-mappings create \
        --service $SERVICE_NAME \
        --domain $DOMAIN \
        --region $REGION
    
    # Get DNS records
    print_info "Getting DNS configuration..."
    RECORDS=$(gcloud beta run domain-mappings describe $DOMAIN --region $REGION --format="value(status.resourceRecords[].name,status.resourceRecords[].rrdata)" | tr '\t' ' ')
    
    print_success "Domain mapping created!"
    print_warning "IMPORTANT: Add these DNS records to your domain:"
    echo ""
    echo "$RECORDS" | while read record; do
        if [[ -n "$record" ]]; then
            echo "  $record"
        fi
    done
    echo ""
    print_info "After adding DNS records, HTTPS will be automatically provisioned by Google"
    print_info "SSL certificate provisioning may take 10-60 minutes"
fi

# Show final status
print_success "Deployment completed!"
echo ""
print_info "Service Details:"
echo "  Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Project: $PROJECT_ID"
if [[ "$BUILD_ONLY" != true ]]; then
    echo "  URL: $SERVICE_URL"
fi
if [[ "$SETUP_DOMAIN" == true ]]; then
    echo "  Custom Domain: https://$DOMAIN"
    echo "  SSL Status: Automatic (will be ready in 10-60 minutes)"
fi
echo ""
print_info "Useful commands:"
echo "  Check logs: gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "  Update env: gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars KEY=VALUE"
echo "  Check domain: gcloud beta run domain-mappings describe $DOMAIN --region $REGION"
echo ""