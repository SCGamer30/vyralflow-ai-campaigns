from fastapi import APIRouter, Depends
from datetime import datetime

from app.models.response import HealthCheckResponse
from app.core.config import settings
from app.core.orchestrator import campaign_orchestrator
from app.core.database import db_manager
from app.services.firestore_service import firestore_service
from app.api.dependencies import get_orchestrator
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    Returns the health status of the application and its dependencies.
    """
    try:
        # Get orchestrator health
        orchestrator_health = await campaign_orchestrator.health_check()
        
        # Get database health
        db_health = await db_manager.health_check()
        
        # Determine overall status
        overall_status = "healthy"
        if orchestrator_health.get('orchestrator') != 'healthy':
            overall_status = "degraded"
        if db_health.get('status') != 'healthy':
            overall_status = "unhealthy"
        
        # Check agent statuses
        agent_statuses = {}
        if 'agents' in orchestrator_health:
            for agent_name, agent_health in orchestrator_health['agents'].items():
                agent_statuses[agent_name] = agent_health.get('status', 'unknown')
        
        services = {
            'orchestrator': orchestrator_health.get('orchestrator', 'unknown'),
            'database': db_health.get('status', 'unknown'),
            'firestore': 'healthy' if db_health.get('status') == 'healthy' else 'unhealthy',
            **agent_statuses
        }
        
        response = HealthCheckResponse(
            status=overall_status,
            version=settings.version,
            timestamp=datetime.utcnow().isoformat(),
            services=services
        )
        
        logger.debug(f"Health check completed: {overall_status}")
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version=settings.version,
            timestamp=datetime.utcnow().isoformat(),
            services={"error": str(e)}
        )


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with comprehensive system information.
    """
    try:
        # Get orchestrator health
        orchestrator_health = await campaign_orchestrator.health_check()
        
        # Get database health
        db_health = await db_manager.health_check()
        
        # Get active campaigns
        active_campaigns = await campaign_orchestrator.get_active_campaigns()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "environment": {
                "debug": settings.debug,
                "project_id": settings.google_cloud_project
            },
            "orchestrator": orchestrator_health,
            "database": db_health,
            "active_campaigns": {
                "count": len(active_campaigns),
                "campaign_ids": active_campaigns
            },
            "configuration": {
                "timeout_seconds": "varies by agent",
                "rate_limiting": f"{settings.rate_limit_requests_per_minute} requests/minute"
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/agents")
async def agents_health_check(
    orchestrator = Depends(get_orchestrator)
):
    """
    Check health status of all agents.
    """
    try:
        health = await orchestrator.health_check()
        
        agents_status = health.get('agents', {})
        
        return {
            "status": "healthy" if all(
                agent.get('status') == 'healthy' 
                for agent in agents_status.values()
            ) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": agents_status,
            "total_agents": len(agents_status)
        }
        
    except Exception as e:
        logger.error(f"Agents health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/readiness")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 if the service is ready to accept requests.
    """
    try:
        # Quick health checks
        orchestrator_health = await campaign_orchestrator.health_check()
        
        if orchestrator_health.get('orchestrator') == 'healthy':
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            logger.warning("Service not ready - orchestrator unhealthy")
            return {"status": "not_ready", "reason": "orchestrator_unhealthy"}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}


@router.get("/liveness")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the service is alive (basic functionality working).
    """
    try:
        # Very basic check - just return success if we can respond
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return {"status": "dead", "error": str(e)}