import time
import hashlib
import re
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Fallback for older FastAPI versions
    from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for Qrow IQ"""
    
    def __init__(self, app, rate_limit: int = None, window: int = 60):
        super().__init__(app)
        # Use config rate limit if not specified, with fallback to 1000 for development
        if rate_limit is None:
            try:
                from config import settings
                self.rate_limit = settings.API_RATE_LIMIT
            except ImportError:
                self.rate_limit = 1000  # Default for development
        else:
            self.rate_limit = rate_limit
        self.window = window
        self.requests: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Rate limiting
        client_ip = self._get_client_ip(request)
        rate_limit_info = self._check_rate_limit(client_ip)
        
        if not rate_limit_info['allowed']:
            # Calculate retry after time
            retry_after = int(rate_limit_info.get('retry_after', 60))
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after,
                    "limit": self.rate_limit,
                    "window": self.window,
                    "current_requests": rate_limit_info.get('current_requests', 0)
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": str(max(0, self.rate_limit - rate_limit_info.get('current_requests', 0))),
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                }
            )
        
        # Security headers
        response = await call_next(request)
        self._add_security_headers(response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> dict:
        """Check if client has exceeded rate limit"""
        now = time.time()
        
        # Clean old requests outside the window
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if now - req_time < self.window
            ]
        else:
            self.requests[client_ip] = []
        
        current_requests = len(self.requests[client_ip])
        
        # Check if limit exceeded
        if current_requests >= self.rate_limit:
            # Calculate when the oldest request will expire
            if self.requests[client_ip]:
                oldest_request = min(self.requests[client_ip])
                retry_after = int(self.window - (now - oldest_request))
            else:
                retry_after = self.window
                
            return {
                'allowed': False,
                'current_requests': current_requests,
                'retry_after': retry_after
            }
        
        # Add current request
        self.requests[client_ip].append(now)
        return {
            'allowed': True,
            'current_requests': current_requests + 1
        }
    
    def _add_security_headers(self, response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com; "
            "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove potentially dangerous HTML tags"""
        dangerous_tags = re.compile(r'<script.*?</script>|<iframe.*?</iframe>|<object.*?</object>', re.IGNORECASE | re.DOTALL)
        return dangerous_tags.sub('', text)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """Check password strength"""
        return {
            "length": len(password) >= 8,
            "uppercase": bool(re.search(r'[A-Z]', password)),
            "lowercase": bool(re.search(r'[a-z]', password)),
            "numbers": bool(re.search(r'\d', password)),
            "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        ext = filename.lower().split('.')[-1]
        return ext in allowed_extensions

class SQLInjectionProtection:
    """SQL injection protection utilities"""
    
    @staticmethod
    def contains_sql_keywords(text: str) -> bool:
        """Check if text contains SQL keywords (basic protection)"""
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'EXEC', 'EXECUTE', 'UNION', 'OR', 'AND', '--', '/*', '*/'
        ]
        text_upper = text.upper()
        return any(keyword in text_upper for keyword in sql_keywords)
    
    @staticmethod
    def sanitize_sql_input(text: str) -> str:
        """Basic SQL input sanitization"""
        if SQLInjectionProtection.contains_sql_keywords(text):
            raise ValueError("Input contains potentially dangerous SQL keywords")
        return text.strip()

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, List[float]] = {}

def get_rate_limit_info(client_ip: str) -> Dict[str, any]:
    """Get rate limit information for a client"""
    now = time.time()
    window = 60  # 1 minute window
    
    if client_ip in rate_limit_storage:
        # Clean old requests
        rate_limit_storage[client_ip] = [
            req_time for req_time in rate_limit_storage[client_ip] 
            if now - req_time < window
        ]
        
        return {
            "requests": len(rate_limit_storage[client_ip]),
            "limit": 100,
            "window": window,
            "remaining": max(0, 100 - len(rate_limit_storage[client_ip]))
        }
    
    return {
        "requests": 0,
        "limit": 100,
        "window": window,
        "remaining": 100
    }
