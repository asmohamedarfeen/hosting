"""
URL Utility Functions
Provides dynamic URL generation based on request context
"""
import os
from fastapi import Request
from typing import Optional
from config import settings

def get_base_url(request: Optional[Request] = None) -> str:
    """
    Get the base URL for the application.
    Priority:
    1. BASE_URL environment variable (for production)
    2. Request URL (if request is provided)
    3. Default localhost (development)
    """
    # Check for explicit BASE_URL environment variable (highest priority)
    base_url = os.getenv("BASE_URL")
    if base_url:
        return base_url.rstrip('/')
    
    # If request is provided, use it to determine the base URL
    if request:
        # Get scheme (http/https)
        scheme = request.url.scheme
        
        # Get host from request
        host = request.url.hostname
        
        # Get port if not standard (80 for http, 443 for https)
        port = request.url.port
        if port and port not in [80, 443]:
            return f"{scheme}://{host}:{port}"
        else:
            return f"{scheme}://{host}"
    
    # Fallback to environment-based detection
    if settings.ENVIRONMENT == "production":
        # In production, try to get from environment
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url.rstrip('/')
        
        # Try other common environment variables
        for env_var in ["APP_URL", "SITE_URL", "PUBLIC_URL"]:
            url = os.getenv(env_var)
            if url:
                return url.rstrip('/')
    
    # Default fallback for development
    return f"http://localhost:{settings.PORT}"

def get_redirect_uri(request: Optional[Request] = None, path: str = "/auth/google/callback") -> str:
    """
    Get the OAuth redirect URI dynamically.
    """
    base_url = get_base_url(request)
    return f"{base_url}{path}"

def build_url(request: Optional[Request] = None, path: str = "") -> str:
    """
    Build a full URL from a path.
    """
    base_url = get_base_url(request)
    # Ensure path starts with /
    if path and not path.startswith('/'):
        path = '/' + path
    return f"{base_url}{path}"

