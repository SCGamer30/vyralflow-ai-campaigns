from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time

from app.core.config import settings
from app.core.orchestrator import campaign_orchestrator
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Security scheme (optional for future authentication)
security = HTTPBearer(auto_error=False)


async def get_orchestrator():
    """Dependency to get the campaign orchestrator."""
    return campaign_orchestrator


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user from authentication token.
    Currently returns None (no authentication required).
    This can be extended for future authentication needs.
    """
    # For now, no authentication is required
    # This dependency can be extended when authentication is needed
    return None


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def __call__(self, request: Request):
        """Rate limiting dependency."""
        client_ip = request.client.host
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        # Clean old entries (keep last 2 minutes)
        self.requests = {
            key: value for key, value in self.requests.items()
            if key[1] >= minute_window - 1
        }
        
        # Count requests in current minute
        key = (client_ip, minute_window)
        request_count = self.requests.get(key, 0)
        
        if request_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Increment request count
        self.requests[key] = request_count + 1
        
        return True


# Rate limiter instances
rate_limiter = RateLimiter(requests_per_minute=settings.rate_limit_requests_per_minute)


async def validate_campaign_id(campaign_id: str) -> str:
    """Validate campaign ID format."""
    if not campaign_id or not campaign_id.startswith('camp_'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    return campaign_id


async def check_service_health():
    """Check if all services are healthy."""
    try:
        health = await campaign_orchestrator.health_check()
        if health.get('orchestrator') != 'healthy':
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )
        return True
    except Exception as e:
        logger.error(f"Service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )


async def log_request(request: Request):
    """Log incoming requests for monitoring."""
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host}"
    )
    return True