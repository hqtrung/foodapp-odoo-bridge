#!/bin/bash
# FoodOrder Bridge API Backup Script

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
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="foodorder-backup-$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

print_info "Starting backup process..."

# Backup cache data
if [[ -d "cache" ]]; then
    print_info "Backing up cache data..."
    tar -czf "$BACKUP_DIR/$BACKUP_NAME-cache.tar.gz" cache/
    print_success "Cache backup completed"
else
    print_warning "Cache directory not found, skipping..."
fi

# Backup images
if [[ -d "public/images" ]]; then
    print_info "Backing up image files..."
    tar -czf "$BACKUP_DIR/$BACKUP_NAME-images.tar.gz" public/images/
    print_success "Images backup completed"
else
    print_warning "Images directory not found, skipping..."
fi

# Backup configuration
print_info "Backing up configuration files..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME-config.tar.gz" \
    --exclude='.env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    .env.example app/ deploy/ scripts/ requirements.txt Dockerfile docker-compose*.yml .dockerignore

print_success "Configuration backup completed"

# Create backup manifest
cat > "$BACKUP_DIR/$BACKUP_NAME-manifest.txt" << EOF
FoodOrder Bridge API Backup Manifest
Created: $(date)
Backup Name: $BACKUP_NAME

Files included:
- $BACKUP_NAME-cache.tar.gz (cache data)
- $BACKUP_NAME-images.tar.gz (image files)  
- $BACKUP_NAME-config.tar.gz (application code and config)
- $BACKUP_NAME-manifest.txt (this file)

Restore Instructions:
1. Stop the application: docker-compose down
2. Extract cache: tar -xzf $BACKUP_NAME-cache.tar.gz
3. Extract images: tar -xzf $BACKUP_NAME-images.tar.gz
4. Extract config: tar -xzf $BACKUP_NAME-config.tar.gz
5. Update .env file with your credentials
6. Restart: docker-compose up -d
EOF

print_success "Backup manifest created"

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR"/"$BACKUP_NAME"* | awk '{sum+=$1} END {print sum}')

print_success "Backup completed successfully!"
print_info "Backup location: $BACKUP_DIR/"
print_info "Backup files:"
ls -la "$BACKUP_DIR"/"$BACKUP_NAME"*

# Cleanup old backups (keep last 5)
print_info "Cleaning up old backups (keeping last 5)..."
cd "$BACKUP_DIR"
ls -t foodorder-backup-*-manifest.txt 2>/dev/null | tail -n +6 | while read manifest; do
    backup_prefix=${manifest%-manifest.txt}
    print_info "Removing old backup: $backup_prefix"
    rm -f "$backup_prefix"*
done
cd ..

print_success "Backup process completed!"
echo ""