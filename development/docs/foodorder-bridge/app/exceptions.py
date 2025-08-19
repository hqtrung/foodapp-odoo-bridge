"""
Custom exceptions for the FoodOrder Bridge API
"""
from typing import Optional


class FoodOrderBridgeException(Exception):
    """Base exception for FoodOrder Bridge API"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class CacheException(FoodOrderBridgeException):
    """Exception raised when cache operations fail"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, status_code=503, details=details)


class OdooConnectionException(FoodOrderBridgeException):
    """Exception raised when Odoo connection fails"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, status_code=502, details=details)


class AuthenticationException(FoodOrderBridgeException):
    """Exception raised when authentication fails"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, status_code=401, details=details)


class TranslationException(FoodOrderBridgeException):
    """Exception raised when translation operations fail"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, status_code=503, details=details)


class ResourceNotFoundException(FoodOrderBridgeException):
    """Exception raised when requested resource is not found"""
    def __init__(self, resource_type: str, resource_id: str, details: Optional[str] = None):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, status_code=404, details=details)


class ValidationException(FoodOrderBridgeException):
    """Exception raised when input validation fails"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, status_code=422, details=details)