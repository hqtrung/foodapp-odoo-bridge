# Google Cloud Run Deployment Guide

Deploy FoodOrder Bridge API to Google Cloud Run with custom domain and HTTPS.

## 🚀 **Quick Deployment**

### **Prerequisites:**
- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Domain `api.patedeli.com` (you control DNS)

### **One-Command Deployment:**
```bash
./scripts/deploy-gcp.sh
```

### **Custom Domain Setup:**
```bash
./scripts/deploy-gcp.sh --setup-domain
```

## 📋 **Deployment Configuration**

### **Resources (Optimized for Cache Service):**
- **Memory:** 512MB (minimal for caching)
- **CPU:** 0.5 vCPU (sufficient for API calls)
- **Concurrency:** 100 requests/instance
- **Max Instances:** 3 (cost-effective scaling)
- **Region:** `asia-southeast1` (Singapore)

### **Estimated Cost:**
- **Light usage:** ~$2-5/month
- **Medium usage:** ~$10-15/month
- **Heavy usage:** ~$20-30/month

## 🔧 **Step-by-Step Setup**

### **1. Initial Deployment**
```bash
# Build and deploy in one command
./scripts/deploy-gcp.sh

# Or step by step:
./scripts/deploy-gcp.sh --build-only   # Build image first
./scripts/deploy-gcp.sh --deploy-only  # Then deploy
```

### **2. Setup Custom Domain**
```bash
# Create domain mapping
./scripts/deploy-gcp.sh --setup-domain

# The script will show DNS records to add:
# Add these to your domain's DNS:
#   api.patedeli.com. CNAME ghs.googlehosted.com.
```

### **3. Configure DNS**
Add DNS records shown by the script to your domain provider:

**Example DNS Configuration:**
```
Type: CNAME
Name: api
Value: ghs.googlehosted.com.
TTL: 300
```

### **4. Verify HTTPS**
After DNS propagation (5-60 minutes):
```bash
curl https://api.patedeli.com/health
```

## 🛠️ **Management Commands**

### **View Logs:**
```bash
gcloud run services logs read foodorder-bridge --region asia-southeast1 --follow
```

### **Update Environment Variables:**
```bash
gcloud run services update foodorder-bridge \
  --region asia-southeast1 \
  --set-env-vars ODOO_API_KEY=new_key_here
```

### **Scale Resources:**
```bash
# Increase memory if needed
gcloud run services update foodorder-bridge \
  --region asia-southeast1 \
  --memory 1Gi \
  --cpu 1
```

### **Check Service Status:**
```bash
gcloud run services describe foodorder-bridge --region asia-southeast1
```

### **Check Domain Status:**
```bash
gcloud run domain-mappings describe api.patedeli.com --region asia-southeast1
```

## 🔒 **Security Features**

### **Automatic HTTPS:**
- Google-managed SSL certificates
- Automatic renewal
- TLS 1.2+ enforcement

### **Environment Variables:**
- Secure storage of Odoo credentials
- No secrets in Docker image
- Runtime configuration

### **Access Control:**
- Public API endpoints
- Can be restricted with IAM if needed

## 📊 **Monitoring**

### **Built-in Monitoring:**
- Cloud Run metrics (requests, latency, errors)
- Cloud Logging integration
- Uptime monitoring

### **Health Check:**
```bash
# Check API health
curl https://api.patedeli.com/health

# Check cache status
curl https://api.patedeli.com/api/v1/cache/status
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Build Fails:**
   ```bash
   # Check build logs
   gcloud builds log --region=global $(gcloud builds list --limit=1 --format="value(id)")
   ```

2. **Service Won't Start:**
   ```bash
   # Check service logs
   gcloud run services logs read foodorder-bridge --region asia-southeast1
   ```

3. **Domain Not Working:**
   ```bash
   # Check DNS propagation
   nslookup api.patedeli.com
   
   # Check domain mapping
   gcloud run domain-mappings describe api.patedeli.com --region asia-southeast1
   ```

4. **Environment Variables:**
   ```bash
   # List current env vars
   gcloud run services describe foodorder-bridge --region asia-southeast1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
   ```

## ⚡ **Performance Optimization**

### **For Light Traffic:**
```bash
# Minimal setup (current configuration)
--memory 512Mi --cpu 0.5 --max-instances 3
```

### **For Heavy Traffic:**
```bash
# Scale up resources
gcloud run services update foodorder-bridge \
  --region asia-southeast1 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 1
```

## 🔄 **CI/CD Integration**

### **Manual Deployment:**
```bash
# Full deployment
./scripts/deploy-gcp.sh

# Just rebuild and deploy
./scripts/deploy-gcp.sh --build-only
./scripts/deploy-gcp.sh --deploy-only
```

### **Automated Deployment:**
Use the included `cloudbuild.yaml` for GitHub Actions or Cloud Build triggers.

## 📈 **Scaling Strategy**

The current configuration is optimized for a caching service:

- **Auto-scales to zero** when no traffic (cost-effective)
- **Scales up automatically** with traffic
- **Maximum 3 instances** prevents runaway costs
- **100 concurrent requests** per instance (suitable for cache API)

For high-traffic scenarios, increase `max-instances` and `memory` as needed.

## 🌐 **Final URLs**

After successful deployment:

- **API Documentation:** https://api.patedeli.com/docs
- **Health Check:** https://api.patedeli.com/health
- **Categories:** https://api.patedeli.com/api/v1/menu/categories
- **Products:** https://api.patedeli.com/api/v1/menu/products
- **Cache Reload:** https://api.patedeli.com/api/v1/cache/reload

All endpoints automatically have **HTTPS** with Google-managed certificates! 🔒