from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Odoo connection settings
    ODOO_URL: str = "https://your-odoo-instance.com"
    ODOO_DB: str = "your_database_name"
    ODOO_USERNAME: str = "your_username@company.com"
    ODOO_PASSWORD: str = ""  # Optional - use if not using API key
    ODOO_API_KEY: str = ""   # Recommended - more secure than password
    
    # API settings
    API_TITLE: str = "FoodOrder Bridge API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FastAPI bridge for FoodOrder PWA with Odoo 18 POS integration"
    
    # Cache settings
    CACHE_DIR: str = "cache"
    IMAGES_DIR: str = "public/images"
    
    # Security settings - CORS configuration
    CORS_ALLOW_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "https://*.patedeli.com",  # Handled via regex pattern in main.py
        "https://patedeli.com"     # Root domain handled directly
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Additional security settings
    MAX_REQUESTS_PER_MINUTE: int = 100
    REQUEST_TIMEOUT_SECONDS: int = 30
    CONNECTION_POOL_SIZE: int = 10
    
    # Cache settings
    CACHE_TTL_HOURS: int = 24
    FIRESTORE_COLLECTION_PREFIX: str = "foodorder_cache"
    
    # Translation settings
    ENABLE_TRANSLATION: bool = True
    DEFAULT_LANGUAGE: str = "vi"
    SUPPORTED_LANGUAGES: list = ["vi", "en", "fr", "it", "es", "zh", "zh-TW", "th", "ja"]
    GOOGLE_CLOUD_PROJECT: str = ""  # Required for Translation API and Vertex AI
    TRANSLATION_CACHE_TTL_DAYS: int = 7
    
    # Translation settings - Vertex AI Gemini 2.0 Flash ONLY
    USE_VERTEX_TRANSLATION: bool = True  # Use Vertex AI exclusively 
    TRANSLATION_FALLBACK_ENABLED: bool = False  # No fallback - Vertex AI only
    VERTEX_AI_LOCATION: str = "us-central1"  # Vertex AI region
    VERTEX_AI_MODEL: str = "gemini-2.5-flash"  # Model: gemini-2.5-flash (fast) or gemini-2.5-pro (highest quality)
    VERTEX_TRANSLATION_BATCH_SIZE: int = 25  # Optimal batch size for Gemini
    VERTEX_TRANSLATION_TEMPERATURE: float = 0.2  # Lower = more consistent translations
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_ACCESS_LOGS: bool = True
    
    # Performance settings
    MAX_IMAGE_SIZE_BYTES: int = 5242880  # 5MB
    MAX_TRANSLATION_BATCH_SIZE: int = 50
    CACHE_CLEANUP_INTERVAL_HOURS: int = 24
    
    # Development settings
    DEBUG: bool = False
    RELOAD: bool = False
    
    # Health check settings
    HEALTH_CHECK_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()