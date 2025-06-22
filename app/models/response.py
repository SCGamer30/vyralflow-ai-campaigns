from pydantic import BaseModel
from typing import Any, Dict, Optional, List


class APIResponse(BaseModel):
    """Standard API response model."""
    
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = "healthy"
    version: str
    timestamp: str
    services: Dict[str, str] = {}


class AgentStatusResponse(BaseModel):
    """Individual agent status response."""
    
    agent_name: str
    status: str
    is_healthy: bool
    last_execution: Optional[str] = None
    error_count: int = 0