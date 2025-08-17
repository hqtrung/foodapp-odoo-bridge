#!/bin/bash
# FoodOrder Bridge API Monitoring Script

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
API_URL="http://localhost:8000"
CHECK_INTERVAL=30
LOG_FILE="monitoring.log"

# Function to check service health
check_health() {
    local url="$1"
    local service="$2"
    
    if curl -s -f "$url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get service stats
get_stats() {
    echo "=============================================="
    echo "FoodOrder Bridge API - System Status"
    echo "Timestamp: $(date)"
    echo "=============================================="
    
    # API Health
    if check_health "$API_URL/health" "API"; then
        print_success "API: Healthy"
        
        # Get API info
        api_info=$(curl -s "$API_URL/health" 2>/dev/null || echo "{}")
        echo "API Info: $api_info"
    else
        print_error "API: Unhealthy"
    fi
    
    echo ""
    
    # Docker containers status
    print_info "Docker Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=foodorder" 2>/dev/null || print_warning "No foodorder containers found"
    
    echo ""
    
    # Resource usage
    print_info "Resource Usage:"
    if command -v docker >/dev/null 2>&1; then
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" --filter "name=foodorder" 2>/dev/null || print_warning "Cannot get Docker stats"
    fi
    
    echo ""
    
    # Disk usage
    print_info "Disk Usage:"
    if [[ -d "cache" ]]; then
        echo "Cache directory: $(du -sh cache 2>/dev/null || echo 'N/A')"
    fi
    if [[ -d "public/images" ]]; then
        echo "Images directory: $(du -sh public/images 2>/dev/null || echo 'N/A')"
    fi
    
    echo ""
    
    # Recent logs (last 10 lines)
    print_info "Recent API Logs:"
    docker logs --tail 10 foodorder-bridge-api 2>/dev/null || docker logs --tail 10 foodorder-bridge-api-prod 2>/dev/null || print_warning "Cannot get API logs"
    
    echo ""
}

# Function to send alert (placeholder)
send_alert() {
    local message="$1"
    local timestamp=$(date)
    
    echo "[$timestamp] ALERT: $message" >> "$LOG_FILE"
    print_error "ALERT: $message"
    
    # Add your alerting mechanism here (email, Slack, etc.)
    # Example: curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$message"'"}' YOUR_WEBHOOK_URL
}

# Function for continuous monitoring
monitor_continuous() {
    print_info "Starting continuous monitoring (interval: ${CHECK_INTERVAL}s)"
    print_info "Press Ctrl+C to stop"
    
    while true; do
        # Check API health
        if ! check_health "$API_URL/health" "API"; then
            send_alert "API is down or unhealthy"
        fi
        
        # Check if containers are running
        if ! docker ps --filter "name=foodorder" --filter "status=running" --quiet | grep -q .; then
            send_alert "No foodorder containers are running"
        fi
        
        # Log status
        echo "[$(date)] Health check completed" >> "$LOG_FILE"
        
        sleep "$CHECK_INTERVAL"
    done
}

# Show help
show_help() {
    echo "FoodOrder Bridge API Monitoring Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status      Show current system status (default)"
    echo "  monitor     Start continuous monitoring"
    echo "  logs        Show recent application logs"
    echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  API_URL     Override API URL (default: http://localhost:8000)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Show status once"
    echo "  $0 monitor                  # Start continuous monitoring"
    echo "  API_URL=https://api.domain.com $0 status  # Check production API"
    echo ""
}

# Main script logic
case "${1:-status}" in
    "status")
        get_stats
        ;;
    "monitor")
        monitor_continuous
        ;;
    "logs")
        print_info "Application Logs:"
        docker logs -f foodorder-bridge-api 2>/dev/null || docker logs -f foodorder-bridge-api-prod 2>/dev/null || print_error "Cannot get logs"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac