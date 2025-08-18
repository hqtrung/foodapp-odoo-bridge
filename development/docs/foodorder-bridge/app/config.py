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
    
    # Security settings
    ALLOWED_HOSTS: list = ["*"]
    
    # Cache settings
    CACHE_TTL_HOURS: int = 24
    FIRESTORE_COLLECTION_PREFIX: str = "foodorder_cache"
    
    # Translation settings
    ENABLE_TRANSLATION: bool = True
    DEFAULT_LANGUAGE: str = "vi"
    SUPPORTED_LANGUAGES: list = ["vi", "en", "zh", "zh-TW", "th"]
    GOOGLE_CLOUD_PROJECT: str = ""  # Required for Translation API
    TRANSLATION_CACHE_TTL_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()