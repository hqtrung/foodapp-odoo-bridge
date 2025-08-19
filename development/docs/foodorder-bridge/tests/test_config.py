"""
Tests for configuration management
"""
import pytest
from app.config import Settings, get_settings


def test_settings_default_values():
    """Test that settings have sensible defaults"""
    settings = Settings()
    
    # Test default values (allowing for environment customization)
    assert "FoodOrder Bridge API" in settings.API_TITLE
    assert settings.API_VERSION == "1.0.0"
    assert settings.CACHE_TTL_HOURS == 24
    assert settings.DEFAULT_LANGUAGE == "vi"
    assert "vi" in settings.SUPPORTED_LANGUAGES
    assert "en" in settings.SUPPORTED_LANGUAGES


def test_cors_configuration():
    """Test CORS configuration"""
    settings = Settings()
    
    # Should not contain wildcard by default
    assert "*" not in settings.CORS_ALLOW_ORIGINS
    assert len(settings.CORS_ALLOW_ORIGINS) > 0
    assert settings.CORS_ALLOW_CREDENTIALS is True


def test_security_settings():
    """Test security-related settings"""
    settings = Settings()
    
    # Rate limiting should be configured
    assert settings.MAX_REQUESTS_PER_MINUTE > 0
    assert settings.REQUEST_TIMEOUT_SECONDS > 0
    assert settings.CONNECTION_POOL_SIZE > 0


def test_get_settings_caching():
    """Test that get_settings returns cached instance"""
    settings1 = get_settings()
    settings2 = get_settings()
    
    # Should be the same instance due to LRU cache
    assert settings1 is settings2


def test_supported_languages():
    """Test supported languages configuration"""
    settings = Settings()
    
    # Should have at least basic languages
    required_languages = ['vi', 'en']
    for lang in required_languages:
        assert lang in settings.SUPPORTED_LANGUAGES
    
    # Should have reasonable number of languages
    assert len(settings.SUPPORTED_LANGUAGES) >= 2