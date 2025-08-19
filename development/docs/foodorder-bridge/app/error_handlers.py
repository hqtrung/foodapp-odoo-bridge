"""
Error handlers for the FoodOrder Bridge API
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from .exceptions import FoodOrderBridgeException

logger = logging.getLogger(__name__)


async def foodorder_exception_handler(request: Request, exc: FoodOrderBridgeException):
    """Handle custom FoodOrder Bridge exceptions"""
    logger.error(
        f"FoodOrderBridgeException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
            "details": exc.details
        }
    )
    
    response_data = {
        "error": exc.message,
        "status_code": exc.status_code,
        "type": exc.__class__.__name__
    }
    
    # Only include details in development
    if exc.details and logger.level == logging.DEBUG:
        response_data["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions without exposing sensitive information"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "url": str(request.url),
            "method": request.method,
            "exception_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal error occurred. Please try again later.",
            "status_code": 500,
            "type": "InternalServerError"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "type": "HTTPException"
        }
    )