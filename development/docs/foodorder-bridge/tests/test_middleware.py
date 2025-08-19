"""
Tests for security and rate limiting middleware
"""
import pytest
import time
from unittest.mock import Mock, AsyncMock
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.middleware import SecurityHeadersMiddleware, RateLimitingMiddleware


class MockApp:
    """Mock ASGI application for testing middleware"""
    
    def __init__(self, response_status=200):
        self.response_status = response_status
    
    async def __call__(self, request):
        return Response("OK", status_code=self.response_status)


@pytest.fixture
def mock_request():
    """Create a mock request object"""
    request = Mock(spec=Request)
    request.url.path = "/api/v1/products"
    request.client.host = "127.0.0.1"
    request.headers.get.return_value = None
    return request


@pytest.mark.asyncio
async def test_security_headers_middleware():
    """Test that security headers are added to responses"""
    app = MockApp()
    middleware = SecurityHeadersMiddleware(app)
    
    # Mock request
    request = Mock(spec=Request)
    
    # Mock call_next function
    async def call_next(req):
        return Response("OK")
    
    response = await middleware.dispatch(request, call_next)
    
    # Check that security headers are present
    expected_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options", 
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Referrer-Policy",
        "Content-Security-Policy"
    ]
    
    for header in expected_headers:
        assert header in response.headers


@pytest.mark.asyncio
async def test_rate_limiting_middleware_allows_normal_traffic():
    """Test that rate limiting allows normal traffic"""
    app = MockApp()
    middleware = RateLimitingMiddleware(app, max_requests=10, window_seconds=60)
    
    # Mock request
    request = Mock(spec=Request)
    request.url.path = "/api/v1/products"
    request.client.host = "127.0.0.1"
    request.headers.get.return_value = None
    
    # Mock call_next function
    async def call_next(req):
        return Response("OK")
    
    # Should allow normal request
    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 200
    
    # Check rate limit headers are added
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


@pytest.mark.asyncio
async def test_rate_limiting_middleware_blocks_excessive_requests():
    """Test that rate limiting blocks excessive requests"""
    app = MockApp()
    middleware = RateLimitingMiddleware(app, max_requests=2, window_seconds=60)
    
    # Mock request
    request = Mock(spec=Request)
    request.url.path = "/api/v1/products"
    request.client.host = "127.0.0.1"
    request.headers.get.return_value = None
    
    # Mock call_next function
    async def call_next(req):
        return Response("OK")
    
    # First two requests should succeed
    for i in range(2):
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
    
    # Third request should be rate limited
    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.body.decode()


@pytest.mark.asyncio
async def test_rate_limiting_middleware_skips_health_checks():
    """Test that rate limiting skips health check endpoints"""
    app = MockApp()
    middleware = RateLimitingMiddleware(app, max_requests=1, window_seconds=60)
    
    # Mock health check request
    request = Mock(spec=Request)
    request.url.path = "/health"
    request.client.host = "127.0.0.1"
    request.headers.get.return_value = None
    
    # Mock call_next function
    async def call_next(req):
        return Response("OK")
    
    # Multiple health check requests should not be rate limited
    for i in range(5):
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200


def test_rate_limiting_get_client_ip():
    """Test IP address extraction from request headers"""
    middleware = RateLimitingMiddleware(MockApp(), max_requests=10, window_seconds=60)
    
    # Test X-Forwarded-For header
    request = Mock(spec=Request)
    request.headers.get.side_effect = lambda key: {
        'x-forwarded-for': '192.168.1.1, proxy1, proxy2'
    }.get(key.lower())
    request.client.host = "127.0.0.1"
    
    ip = middleware._get_client_ip(request)
    assert ip == "192.168.1.1"
    
    # Test X-Real-IP header
    request = Mock(spec=Request)  # Create fresh request mock
    request.headers.get.side_effect = lambda key: {
        'x-real-ip': '192.168.1.2'
    }.get(key.lower())
    request.client.host = "127.0.0.1"
    
    ip = middleware._get_client_ip(request)
    assert ip == "192.168.1.2"
    
    # Test fallback to client.host
    request = Mock(spec=Request)  # Create fresh request mock
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"
    
    ip = middleware._get_client_ip(request)
    assert ip == "127.0.0.1"


def test_rate_limiting_cleanup():
    """Test cleanup of old entries"""
    middleware = RateLimitingMiddleware(MockApp(), max_requests=10, window_seconds=1)
    
    # Add some old entries
    client_ip = "127.0.0.1"
    current_time = time.time()
    
    middleware.request_counts[client_ip] = {
        'requests': [current_time - 2, current_time - 1.5],  # Old requests
        'first_request': current_time - 2
    }
    
    # Cleanup should remove old entries
    middleware._cleanup_old_entries(current_time)
    
    # Client IP should be removed due to no recent requests
    assert client_ip not in middleware.request_counts