# FoodOrder Bridge API

A FastAPI bridge service that connects the FoodOrder PWA with Odoo 18 POS system, providing cached menu data and image serving capabilities.

## Features

- **JSON-based caching** for POS categories and products
- **Local image storage** with optimization and compression
- **RESTful API** for menu data retrieval
- **Manual cache reload** functionality
- **Static image serving** with optimized delivery
- **CORS support** for frontend integration

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to project directory
cd foodorder-bridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Odoo credentials
nano .env
```

Required environment variables:
```bash
ODOO_URL=https://erp.patedeli.com
ODOO_DB=your_database_name
ODOO_USERNAME=admin

# Use API Key (Recommended - More Secure)
ODOO_API_KEY=your_api_key_here

# OR use Password (Alternative)
# ODOO_PASSWORD=your_password
```

### 3. Start the Server

```bash
# Development server with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Load Initial Cache

```bash
# Test Odoo connection
curl http://localhost:8000/api/v1/cache/test-connection

# Load cache from Odoo
curl -X POST http://localhost:8000/api/v1/cache/reload
```

## API Endpoints

### Menu Data
- `GET /api/v1/categories` - Get all POS categories
- `GET /api/v1/products` - Get all POS products
- `GET /api/v1/products?category_id=5` - Get products by category
- `GET /api/v1/products/{product_id}` - Get specific product
- `GET /api/v1/menu/summary` - Get categories with product counts

### Cache Management
- `POST /api/v1/cache/reload` - Reload cache from Odoo
- `GET /api/v1/cache/status` - Get cache metadata
- `GET /api/v1/cache/test-connection` - Test Odoo connection
- `DELETE /api/v1/cache/clear` - Clear cache (development only)

### Static Files
- `GET /images/categories/{id}.jpg` - Category images
- `GET /images/products/{id}.jpg` - Product images

### Utility
- `GET /` - API information and endpoints
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Usage Examples

### Get Categories
```bash
curl http://localhost:8000/api/v1/categories
```

### Get Products by Category
```bash
curl "http://localhost:8000/api/v1/products?category_id=1"
```

### Reload Cache
```bash
curl -X POST http://localhost:8000/api/v1/cache/reload
```

### Check Cache Status
```bash
curl http://localhost:8000/api/v1/cache/status
```

## Cache Structure

### JSON Files
```
cache/
├── categories.json     # POS categories with image URLs
├── products.json      # POS products with image URLs  
└── metadata.json      # Cache timestamps and counts
```

### Images
```
public/images/
├── categories/        # Optimized category images
│   ├── 1.jpg
│   └── 2.jpg
└── products/          # Optimized product images
    ├── 1.jpg
    └── 2.jpg
```

## Image Processing

- **Format**: All images converted to JPEG
- **Size**: Maximum 800x800 pixels
- **Quality**: 85% compression
- **Background**: White background for transparent images
- **Cleanup**: Automatic removal of unused images

## Data Flow

1. **Cache Reload**:
   - Fetches categories and products from Odoo
   - Downloads and optimizes images
   - Saves data to JSON files with image URLs
   - Cleans up unused images

2. **API Requests**:
   - Reads data from JSON cache files
   - Returns structured JSON responses
   - Images served as static files

## Development

### Project Structure
```
foodorder-bridge/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and configuration
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── menu.py            # Menu API endpoints
│   └── services/
│       ├── __init__.py
│       └── odoo_cache_service.py  # Odoo integration and caching
├── cache/                      # JSON cache files (auto-created)
├── public/images/             # Optimized images (auto-created)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

### Adding New Endpoints

1. Add endpoint to `app/controllers/menu.py`
2. Update cache service if needed in `app/services/odoo_cache_service.py`
3. Test with the interactive docs at `http://localhost:8000/docs`

### Debugging

- Check logs in terminal where server is running
- Use `/api/v1/cache/test-connection` to verify Odoo connectivity
- Check `/api/v1/cache/status` for cache health
- Inspect JSON files in `cache/` directory

## Production Deployment

1. **Environment Variables**: Set production Odoo credentials
2. **Static Files**: Configure web server to serve `/images` efficiently
3. **CORS**: Update `ALLOWED_HOSTS` to specific domains
4. **Process Manager**: Use gunicorn or supervisor for production
5. **Monitoring**: Add logging and health checks
6. **Cache Strategy**: Consider automatic cache refresh schedule

### Production Command
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Integration with Frontend

### Next.js Example
```javascript
const API_BASE_URL = 'http://localhost:8000';

// Fetch categories
const categories = await fetch(`${API_BASE_URL}/api/v1/categories`);

// Display product with image
const ProductCard = ({ product }) => (
  <div>
    <img src={`${API_BASE_URL}${product.image_url}`} alt={product.name} />
    <h3>{product.name}</h3>
    <p>{product.list_price} VND</p>
  </div>
);
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Check Odoo URL and credentials in `.env`
2. **Authentication Failed**: Verify Odoo username and password
3. **Empty Cache**: Run `POST /api/v1/cache/reload` first
4. **Image Not Loading**: Check if image exists in `public/images/`
5. **Permission Error**: Ensure write permissions for `cache/` and `public/` directories

### Support

For issues and questions, check the project documentation or create an issue in the project repository.