# FoodOrder Bridge API - Deployment Guide

This guide provides comprehensive instructions for deploying the FoodOrder Bridge API using Docker.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ available RAM
- 10GB+ available disk space

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Required environment variables:
```bash
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username@company.com
ODOO_API_KEY=your_api_key_here
```

### 2. Development Deployment

```bash
# Deploy with helper script
./scripts/deploy.sh

# Or manually with docker-compose
docker-compose up -d
```

Access your API at: http://localhost:8000/docs

### 3. Production Deployment

```bash
# Deploy production environment
./scripts/deploy.sh -e production

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

## 📁 Deployment Options

### Option 1: Local Development

**Best for:** Development, testing, local demos

**Features:**
- Hot reload for code changes
- Debug logging
- Single API instance
- Optional Redis cache
- Source code mounted as volume

**Command:**
```bash
./scripts/deploy.sh
```

**Services:**
- API: http://localhost:8000
- Redis: redis://localhost:6379
- Nginx: http://localhost:80

### Option 2: Production Docker

**Best for:** Production deployments, staging environments

**Features:**
- Multi-stage optimized builds
- Multiple API replicas for load balancing
- SSL termination with Nginx
- Health checks and auto-restart
- Monitoring with Prometheus & Grafana
- Production logging

**Command:**
```bash
./scripts/deploy.sh -e production -b
```

**Services:**
- API: https://your-domain.com
- Nginx: Port 80/443
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

### Option 3: Manual Docker

**Best for:** Custom configurations, CI/CD pipelines

**Build and run:**
```bash
# Build image
docker build -t foodorder-bridge .

# Run container
docker run -d \
  --name foodorder-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/public:/app/public \
  foodorder-bridge
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ODOO_URL` | Odoo instance URL | - | ✅ |
| `ODOO_DB` | Odoo database name | - | ✅ |
| `ODOO_USERNAME` | Odoo username | - | ✅ |
| `ODOO_API_KEY` | Odoo API key | - | ✅ |
| `PORT` | API server port | 8000 | ❌ |
| `HOST` | Server host binding | 0.0.0.0 | ❌ |
| `ENVIRONMENT` | Environment mode | production | ❌ |
| `DEBUG` | Debug mode | false | ❌ |
| `LOG_LEVEL` | Logging level | INFO | ❌ |
| `CACHE_TTL` | Cache TTL in seconds | 3600 | ❌ |

### SSL Configuration (Production)

For production HTTPS, place your SSL certificates in `deploy/ssl/`:
```
deploy/ssl/
├── cert.pem
└── key.pem
```

Or use Let's Encrypt with Certbot:
```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy to deploy directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deploy/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem deploy/ssl/key.pem
```

## 📊 Monitoring & Management

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check all services
./scripts/monitor.sh status
```

### Continuous Monitoring

```bash
# Start monitoring daemon
./scripts/monitor.sh monitor

# View logs
./scripts/monitor.sh logs
```

### Cache Management

```bash
# Reload cache via API
curl -X POST http://localhost:8000/api/v1/cache/reload

# Clear cache files
docker-compose exec foodorder-api rm -rf /app/cache/*
```

## 🔧 Maintenance

### Backup

```bash
# Create backup
./scripts/backup.sh

# Restore from backup
tar -xzf backups/foodorder-backup-YYYYMMDD_HHMMSS-cache.tar.gz
tar -xzf backups/foodorder-backup-YYYYMMDD_HHMMSS-images.tar.gz
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
./scripts/deploy.sh -e production -b

# Or rolling update (zero downtime)
docker-compose -f docker-compose.prod.yml up -d --scale foodorder-api=2
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View API logs only
docker-compose logs -f foodorder-api

# View Nginx logs
docker-compose logs -f nginx
```

## 🐛 Troubleshooting

### Common Issues

1. **API not starting**
   ```bash
   # Check logs
   docker-compose logs foodorder-api
   
   # Check environment
   docker-compose exec foodorder-api env | grep ODOO
   ```

2. **Cache not working**
   ```bash
   # Check cache directory permissions
   ls -la cache/
   
   # Recreate cache
   docker-compose exec foodorder-api rm -rf /app/cache/*
   curl -X POST http://localhost:8000/api/v1/cache/reload
   ```

3. **Images not loading**
   ```bash
   # Check images directory
   ls -la public/images/
   
   # Test image access
   curl http://localhost:8000/images/products/1.jpg
   ```

4. **SSL issues (Production)**
   ```bash
   # Check certificate
   openssl x509 -in deploy/ssl/cert.pem -text -noout
   
   # Test SSL
   curl -I https://your-domain.com
   ```

### Performance Tuning

1. **Increase API replicas:**
   ```yaml
   # In docker-compose.prod.yml
   deploy:
     replicas: 4  # Increase based on load
   ```

2. **Optimize Nginx:**
   ```nginx
   # In deploy/nginx.conf
   worker_processes auto;
   worker_connections 2048;
   ```

3. **Cache optimization:**
   ```bash
   # Increase cache TTL
   CACHE_TTL=7200  # 2 hours
   ```

## 📈 Performance Metrics

### Expected Performance

- **Response time:** < 200ms (cached), < 2s (uncached)
- **Throughput:** 100+ requests/second
- **Memory usage:** ~200MB per instance
- **Cache hit ratio:** > 80%

### Monitoring URLs

- Health check: `/health`
- Metrics: `/metrics` (Prometheus format)
- API docs: `/docs`
- OpenAPI spec: `/openapi.json`

## 🔒 Security Considerations

1. **Environment variables:** Never commit `.env` files
2. **SSL certificates:** Use proper CA-signed certificates in production
3. **Network security:** Restrict access to monitoring endpoints
4. **Updates:** Keep Docker images updated regularly
5. **Backups:** Encrypt backups containing sensitive data

## 📞 Support

- Check logs: `./scripts/monitor.sh logs`
- Health status: `./scripts/monitor.sh status`
- Create backup: `./scripts/backup.sh`
- Restart services: `docker-compose restart`

For additional support, check the application logs and Odoo connectivity.