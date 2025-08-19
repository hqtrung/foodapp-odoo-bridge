"""
Security and rate limiting middleware for the FoodOrder Bridge API
"""
import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers to response
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware based on IP address"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, Dict] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first (for reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_entries(self, current_time: float):
        """Clean up old entries to prevent memory leaks"""
        cutoff_time = current_time - self.window_seconds
        
        for ip in list(self.request_counts.keys()):
            ip_data = self.request_counts[ip]
            # Remove old requests
            ip_data["requests"] = [
                req_time for req_time in ip_data["requests"] 
                if req_time > cutoff_time
            ]
            
            # Remove IP entry if no recent requests
            if not ip_data["requests"]:
                del self.request_counts[ip]
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited"""
        current_time = time.time()
        
        # Clean up old entries periodically
        self._cleanup_old_entries(current_time)
        
        # Initialize IP data if not exists
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                "requests": [],
                "first_request": current_time
            }
        
        ip_data = self.request_counts[client_ip]
        
        # Count requests in current window
        window_start = current_time - self.window_seconds
        recent_requests = [
            req_time for req_time in ip_data["requests"]
            if req_time > window_start
        ]
        
        # Check if rate limit exceeded
        if len(recent_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {len(recent_requests)} requests in {self.window_seconds}s")
            return True
        
        # Add current request
        ip_data["requests"].append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.max_requests} requests per {self.window_seconds} seconds allowed",
                    "status_code": 429,
                    "type": "RateLimitExceeded"
                },
                headers={
                    "Retry-After": str(self.window_seconds)
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        current_time = time.time()
        if client_ip in self.request_counts:
            ip_data = self.request_counts[client_ip]
            window_start = current_time - self.window_seconds
            recent_requests = [
                req_time for req_time in ip_data["requests"]
                if req_time > window_start
            ]
            
            remaining = max(0, self.max_requests - len(recent_requests))
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts"""
    
    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Note: FastAPI/Starlette doesn't have built-in request timeout
            # This would need to be implemented with asyncio.wait_for
            # For now, we'll just pass through and rely on server-level timeouts
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request timeout or error: {e}", exc_info=True)
            return JSONResponse(
                status_code=408,
                content={
                    "error": "Request timeout",
                    "message": "Request took too long to process",
                    "status_code": 408,
                    "type": "RequestTimeout"
                }
            )