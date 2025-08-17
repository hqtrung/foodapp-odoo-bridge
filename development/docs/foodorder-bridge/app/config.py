from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Odoo connection settings
    ODOO_URL: str = "http://localhost:8069"
    ODOO_DB: str = "odoo_database"
    ODOO_USERNAME: str = "admin"
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()