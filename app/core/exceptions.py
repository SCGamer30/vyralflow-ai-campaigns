from typing import Any, Dict, Optional


class VyralflowException(Exception):
    """Base exception for Vyralflow AI application."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class CampaignNotFoundException(VyralflowException):
    """Raised when a campaign is not found."""
    
    def __init__(self, campaign_id: str):
        super().__init__(
            message=f"Campaign with ID '{campaign_id}' not found",
            error_code="CAMPAIGN_NOT_FOUND",
            details={"campaign_id": campaign_id}
        )


class AgentExecutionException(VyralflowException):
    """Raised when an agent fails to execute."""
    
    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            message=f"Agent '{agent_name}' execution failed: {reason}",
            error_code="AGENT_EXECUTION_FAILED",
            details={"agent_name": agent_name, "reason": reason}
        )


class ExternalAPIException(VyralflowException):
    """Raised when external API calls fail."""
    
    def __init__(self, service_name: str, reason: str):
        super().__init__(
            message=f"External API '{service_name}' failed: {reason}",
            error_code="EXTERNAL_API_ERROR",
            details={"service_name": service_name, "reason": reason}
        )


class ValidationException(VyralflowException):
    """Raised when input validation fails."""
    
    def __init__(self, field_name: str, reason: str):
        super().__init__(
            message=f"Validation failed for '{field_name}': {reason}",
            error_code="VALIDATION_ERROR",
            details={"field_name": field_name, "reason": reason}
        )


class DatabaseException(VyralflowException):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database operation '{operation}' failed: {reason}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "reason": reason}
        )