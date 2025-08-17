from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.controllers import menu
from app.config import get_settings

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure public/images directory exists
images_dir = Path("public/images")
images_dir.mkdir(parents=True, exist_ok=True)

# Mount static files directory for images
app.mount("/images", StaticFiles(directory="public/images"), name="images")

# Include routers
app.include_router(menu.router)


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
            "test_connection": "/api/v1/cache/test-connection"
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
        log_level="info"
    )