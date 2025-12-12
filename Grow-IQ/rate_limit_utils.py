"""
Rate limiting utilities for Qrow IQ
Handles rate limit errors gracefully with retry logic
"""

import time
import asyncio
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RateLimitHandler:
    """Handles rate limit errors with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def handle_rate_limit(self, response_data: Dict[str, Any], attempt: int = 1) -> Optional[Dict[str, Any]]:
        """Handle rate limit response and suggest retry strategy"""
        if response_data.get('detail') == 'Rate limit exceeded. Please try again later.':
            retry_after = response_data.get('retry_after', 60)
            current_requests = response_data.get('current_requests', 0)
            limit = response_data.get('limit', 1000)
            
            logger.warning(
                f"Rate limit exceeded: {current_requests}/{limit} requests. "
                f"Retry after {retry_after} seconds. Attempt {attempt}/{self.max_retries}"
            )
            
            if attempt <= self.max_retries:
                # Calculate delay with exponential backoff
                delay = min(retry_after, self.base_delay * (2 ** (attempt - 1)))
                
                logger.info(f"Waiting {delay} seconds before retry...")
                await asyncio.sleep(delay)
                
                return {
                    'should_retry': True,
                    'delay': delay,
                    'attempt': attempt + 1
                }
            else:
                logger.error(f"Max retries ({self.max_retries}) exceeded. Giving up.")
                return {
                    'should_retry': False,
                    'error': 'Max retries exceeded'
                }
        
        return None

def create_retry_request(func, *args, **kwargs):
    """Decorator to automatically retry requests on rate limit errors"""
    async def wrapper(*args, **kwargs):
        handler = RateLimitHandler()
        attempt = 1
        
        while attempt <= handler.max_retries:
            try:
                response = await func(*args, **kwargs)
                
                # Check if it's a rate limit error
                if response.status_code == 429:
                    rate_limit_info = await handler.handle_rate_limit(
                        response.json(), attempt
                    )
                    
                    if rate_limit_info and rate_limit_info['should_retry']:
                        attempt = rate_limit_info['attempt']
                        continue
                    else:
                        return response
                
                return response
                
            except Exception as e:
                logger.error(f"Request failed on attempt {attempt}: {e}")
                if attempt >= handler.max_retries:
                    raise
                attempt += 1
                
                # Wait before retry
                await asyncio.sleep(handler.base_delay * (2 ** (attempt - 1)))
        
        raise Exception("Max retries exceeded")
    
    return wrapper

def get_rate_limit_info(response_headers: Dict[str, str]) -> Dict[str, Any]:
    """Extract rate limit information from response headers"""
    return {
        'limit': int(response_headers.get('X-RateLimit-Limit', 0)),
        'remaining': int(response_headers.get('X-RateLimit-Remaining', 0)),
        'reset': int(response_headers.get('X-RateLimit-Reset', 0)),
        'retry_after': int(response_headers.get('Retry-After', 0))
    }

def is_rate_limited(response_status: int, response_data: Dict[str, Any]) -> bool:
    """Check if response indicates rate limiting"""
    return (
        response_status == 429 and 
        response_data.get('detail') == 'Rate limit exceeded. Please try again later.'
    )

def calculate_retry_delay(response_data: Dict[str, Any], attempt: int = 1, base_delay: float = 1.0) -> float:
    """Calculate retry delay with exponential backoff"""
    retry_after = response_data.get('retry_after', 60)
    exponential_delay = base_delay * (2 ** (attempt - 1))
    
    # Use the smaller of the two delays
    return min(retry_after, exponential_delay)

# Convenience functions for common use cases
async def wait_for_rate_limit(response_data: Dict[str, Any]) -> None:
    """Wait for the specified time when rate limited"""
    retry_after = response_data.get('retry_after', 60)
    logger.info(f"Rate limited. Waiting {retry_after} seconds...")
    await asyncio.sleep(retry_after)

def log_rate_limit_info(response_data: Dict[str, Any], endpoint: str) -> None:
    """Log rate limit information for debugging"""
    logger.info(
        f"Rate limit info for {endpoint}: "
        f"Limit: {response_data.get('limit', 'N/A')}, "
        f"Current: {response_data.get('current_requests', 'N/A')}, "
        f"Retry after: {response_data.get('retry_after', 'N/A')}s"
    )
