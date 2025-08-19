"""
Tests for custom exceptions
"""
import pytest
from app.exceptions import (
    FoodOrderBridgeException,
    CacheException,
    OdooConnectionException,
    AuthenticationException,
    TranslationException,
    ResourceNotFoundException,
    ValidationException
)


def test_base_exception():
    """Test base FoodOrderBridgeException"""
    exc = FoodOrderBridgeException("Test message", status_code=500)
    
    assert str(exc) == "Test message"
    assert exc.message == "Test message"
    assert exc.status_code == 500
    assert exc.details is None


def test_base_exception_with_details():
    """Test base exception with details"""
    exc = FoodOrderBridgeException("Test message", status_code=500, details="Additional info")
    
    assert exc.details == "Additional info"


def test_cache_exception():
    """Test CacheException"""
    exc = CacheException("Cache error")
    
    assert str(exc) == "Cache error"
    assert exc.status_code == 503


def test_odoo_connection_exception():
    """Test OdooConnectionException"""
    exc = OdooConnectionException("Connection failed")
    
    assert str(exc) == "Connection failed"
    assert exc.status_code == 502


def test_authentication_exception():
    """Test AuthenticationException"""
    exc = AuthenticationException("Auth failed")
    
    assert str(exc) == "Auth failed"
    assert exc.status_code == 401


def test_translation_exception():
    """Test TranslationException"""
    exc = TranslationException("Translation failed")
    
    assert str(exc) == "Translation failed"
    assert exc.status_code == 503


def test_resource_not_found_exception():
    """Test ResourceNotFoundException"""
    exc = ResourceNotFoundException("Product", "123")
    
    assert str(exc) == "Product with ID 123 not found"
    assert exc.status_code == 404


def test_validation_exception():
    """Test ValidationException"""
    exc = ValidationException("Invalid input")
    
    assert str(exc) == "Invalid input"
    assert exc.status_code == 422


def test_inheritance():
    """Test that all exceptions inherit from base exception"""
    exceptions = [
        CacheException("test"),
        OdooConnectionException("test"),
        AuthenticationException("test"),
        TranslationException("test"),
        ResourceNotFoundException("Product", "123"),
        ValidationException("test")
    ]
    
    for exc in exceptions:
        assert isinstance(exc, FoodOrderBridgeException)
        assert hasattr(exc, 'message')
        assert hasattr(exc, 'status_code')
        assert hasattr(exc, 'details')