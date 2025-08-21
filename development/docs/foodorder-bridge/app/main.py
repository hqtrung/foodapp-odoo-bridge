from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.controllers import menu, translations
from app.config import get_settings
from app.exceptions import FoodOrderBridgeException
from app.error_handlers import foodorder_exception_handler, general_exception_handler, http_exception_handler
from app.middleware import SecurityHeadersMiddleware, RateLimitingMiddleware, RequestTimeoutMiddleware

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security and rate limiting middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitingMiddleware, 
    max_requests=settings.MAX_REQUESTS_PER_MINUTE, 
    window_seconds=60
)
app.add_middleware(
    RequestTimeoutMiddleware, 
    timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS
)

# Add CORS middleware with secure configuration
# Handle wildcard domains properly
cors_origins = []
allow_origin_regex = None

for origin in settings.CORS_ALLOW_ORIGINS:
    if "*.patedeli.com" in origin:
        # Set regex pattern for patedeli subdomains
        allow_origin_regex = r"https://.*\.patedeli\.com"
    else:
        cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add exception handlers
app.add_exception_handler(FoodOrderBridgeException, foodorder_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Ensure public/images directory exists
images_dir = Path("public/images")
images_dir.mkdir(parents=True, exist_ok=True)

# Mount static files directory for images
app.mount("/images", StaticFiles(directory="public/images"), name="images")

# Include routers
app.include_router(menu.router)
app.include_router(translations.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FoodOrder Bridge API",
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs_url": "/docs",
        "endpoints": {
            "categories": "/api/v1/categories",
            "products": "/api/v1/products",
            "cache_reload": "/api/v1/cache/reload",
            "cache_status": "/api/v1/cache/status",
            "test_connection": "/api/v1/cache/test-connection",
            "translations_v2": "/api/v1/translations-v2",
            "bulk_language_products": "/api/v1/translations-v2/products?language={language}",
            "translation_status_v2": "/api/v1/translations-v2/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "foodorder-bridge",
        "version": settings.API_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=30,
        limit_concurrency=1000,
        limit_max_requests=10000,
        backlog=2048
    )