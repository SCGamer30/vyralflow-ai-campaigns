from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List

from app.models.response import AgentStatusResponse
from app.core.orchestrator import campaign_orchestrator
from app.agents.trend_analyzer import trend_analyzer_agent
from app.agents.content_writer import content_writer_agent
from app.agents.visual_designer import visual_designer_agent
from app.agents.campaign_scheduler import campaign_scheduler_agent
from app.api.dependencies import get_current_user
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", response_model=List[AgentStatusResponse])
async def get_all_agents_status(
    _user = Depends(get_current_user)
):
    """
    Get status of all AI agents in the system.
    
    Returns the current status and health information for each agent:
    - Trend Analyzer Agent
    - Content Writer Agent  
    - Visual Designer Agent
    - Campaign Scheduler Agent
    
    **Response:**
    Array of agent status objects including health information and execution metrics.
    """
    try:
        agents = [
            ("trend_analyzer", trend_analyzer_agent),
            ("content_writer", content_writer_agent), 
            ("visual_designer", visual_designer_agent),
            ("campaign_scheduler", campaign_scheduler_agent)
        ]
        
        agent_statuses = []
        
        for agent_name, agent_instance in agents:
            try:
                health = await agent_instance.health_check()
                agent_info = agent_instance.get_agent_info()
                
                status_response = AgentStatusResponse(
                    agent_name=agent_name,
                    status=health.get('status', 'unknown'),
                    is_healthy=health.get('status') == 'healthy',
                    last_execution=health.get('last_execution'),
                    error_count=0  # Could be extended to track error counts
                )
                
                agent_statuses.append(status_response)
                
            except Exception as e:
                logger.error(f"Failed to get status for {agent_name}: {e}")
                error_status = AgentStatusResponse(
                    agent_name=agent_name,
                    status='error',
                    is_healthy=False,
                    error_count=1
                )
                agent_statuses.append(error_status)
        
        return agent_statuses
        
    except Exception as e:
        logger.error(f"Failed to get agents status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agents status: {str(e)}"
        )


@router.get("/{agent_name}/status")
async def get_agent_status(
    agent_name: str,
    _user = Depends(get_current_user)
):
    """
    Get detailed status of a specific agent.
    
    **Path Parameters:**
    - **agent_name**: Name of the agent (trend_analyzer, content_writer, visual_designer, campaign_scheduler)
    
    **Response:**
    Detailed status information for the specified agent including:
    - Current health status
    - Configuration details
    - Recent execution information
    - Performance metrics
    """
    try:
        # Map agent names to instances
        agent_map = {
            "trend_analyzer": trend_analyzer_agent,
            "content_writer": content_writer_agent,
            "visual_designer": visual_designer_agent, 
            "campaign_scheduler": campaign_scheduler_agent
        }
        
        if agent_name not in agent_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found. Available agents: {list(agent_map.keys())}"
            )
        
        agent_instance = agent_map[agent_name]
        
        # Get agent health and info
        health = await agent_instance.health_check()
        agent_info = agent_instance.get_agent_info()
        
        return {
            "agent_name": agent_name,
            "health": health,
            "info": agent_info,
            "capabilities": {
                "timeout_seconds": agent_info.get('timeout_seconds'),
                "agent_type": agent_info.get('agent_type'),
                "current_status": agent_info.get('status')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status for {agent_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.get("/{agent_name}/info")
async def get_agent_info(
    agent_name: str,
    _user = Depends(get_current_user)
):
    """
    Get detailed information about a specific agent.
    
    **Path Parameters:**
    - **agent_name**: Name of the agent
    
    **Response:**
    Comprehensive information about the agent including:
    - Agent capabilities and purpose
    - Configuration parameters
    - API integrations used
    - Expected input and output formats
    """
    try:
        agent_descriptions = {
            "trend_analyzer": {
                "name": "Trend Analyzer Agent",
                "purpose": "Analyzes social media trends using Google Trends and Reddit API",
                "capabilities": [
                    "Google Trends analysis",
                    "Reddit trend extraction",
                    "Industry-specific trend filtering",
                    "Hashtag recommendations",
                    "Trend confidence scoring"
                ],
                "apis_used": ["Google Trends (pytrends)", "Reddit API", "Fallback data"],
                "output": "Trending topics, hashtags, analysis summary, confidence scores",
                "execution_time": "~60-120 seconds"
            },
            "content_writer": {
                "name": "Content Writer Agent", 
                "purpose": "Generates platform-specific content using Google Gemini AI",
                "capabilities": [
                    "Platform-optimized content generation",
                    "Multiple content variations",
                    "Character limit compliance",
                    "Brand voice adaptation",
                    "Hashtag integration"
                ],
                "apis_used": ["Google Gemini API", "Fallback templates"],
                "output": "Platform-specific content with variations for each target platform",
                "execution_time": "~30-90 seconds"
            },
            "visual_designer": {
                "name": "Visual Designer Agent",
                "purpose": "Suggests visual concepts and finds relevant images",
                "capabilities": [
                    "Image suggestions from Unsplash",
                    "Color palette generation", 
                    "Visual theme analysis",
                    "Style recommendations",
                    "Industry-specific visual guidance"
                ],
                "apis_used": ["Unsplash API", "Fallback placeholder images"],
                "output": "Image suggestions, color palettes, style recommendations",
                "execution_time": "~30-60 seconds"
            },
            "campaign_scheduler": {
                "name": "Campaign Scheduler Agent",
                "purpose": "Optimizes posting times and creates scheduling recommendations",
                "capabilities": [
                    "Platform-specific optimal timing",
                    "Audience behavior analysis",
                    "Coordinated posting sequences",
                    "Industry timing adjustments",
                    "Posting frequency recommendations"
                ],
                "apis_used": ["Built-in scheduling algorithms", "Platform best practices"],
                "output": "Optimal posting times, coordinated schedules, posting sequences",
                "execution_time": "~15-30 seconds"
            }
        }
        
        if agent_name not in agent_descriptions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
        
        return agent_descriptions[agent_name]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent info for {agent_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent info: {str(e)}"
        )


@router.get("/workflow")
async def get_agent_workflow(
    _user = Depends(get_current_user)
):
    """
    Get information about the agent execution workflow.
    
    **Response:**
    Detailed information about how agents work together including:
    - Execution sequence
    - Data flow between agents
    - Dependencies and requirements
    - Total estimated execution time
    """
    try:
        workflow_info = {
            "execution_sequence": [
                {
                    "step": 1,
                    "agent": "trend_analyzer",
                    "description": "Analyzes current trends and generates trend data",
                    "estimated_time": "60-120 seconds",
                    "outputs": ["trending_topics", "trending_hashtags", "analysis_summary"]
                },
                {
                    "step": 2, 
                    "agent": "content_writer",
                    "description": "Creates platform-specific content using trend data",
                    "estimated_time": "30-90 seconds",
                    "inputs_from": ["trend_analyzer"],
                    "outputs": ["platform_content", "content_variations", "hashtags"]
                },
                {
                    "step": 3,
                    "agent": "visual_designer", 
                    "description": "Suggests visual concepts and finds relevant images",
                    "estimated_time": "30-60 seconds",
                    "inputs_from": ["trend_analyzer", "content_writer"],
                    "outputs": ["image_suggestions", "color_palette", "style_recommendations"]
                },
                {
                    "step": 4,
                    "agent": "campaign_scheduler",
                    "description": "Creates optimized posting schedule and timing",
                    "estimated_time": "15-30 seconds", 
                    "inputs_from": ["trend_analyzer", "content_writer", "visual_designer"],
                    "outputs": ["posting_schedule", "optimal_times", "posting_sequence"]
                }
            ],
            "total_estimated_time": "135-300 seconds (2.25-5 minutes)",
            "execution_model": "Sequential (agents run one after another)",
            "error_handling": "Each agent has fallback mechanisms if external APIs fail",
            "progress_tracking": "Real-time progress updates available via status endpoint",
            "data_flow": {
                "description": "Each agent passes its results to subsequent agents",
                "cumulative": "Later agents have access to all previous agent results"
            }
        }
        
        return workflow_info
        
    except Exception as e:
        logger.error(f"Failed to get workflow info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow info: {str(e)}"
        )


@router.post("/health-check")
async def trigger_agents_health_check(
    _user = Depends(get_current_user)
):
    """
    Trigger a comprehensive health check for all agents.
    
    This endpoint performs a deep health check on all agents and their dependencies.
    Use this to verify system readiness before creating campaigns.
    
    **Response:**
    Comprehensive health status for all agents and the orchestrator.
    """
    try:
        # Get comprehensive health check from orchestrator
        health_check = await campaign_orchestrator.health_check()
        
        return {
            "health_check_timestamp": health_check.get('timestamp'),
            "overall_status": "healthy" if health_check.get('orchestrator') == 'healthy' else "degraded",
            "orchestrator": health_check.get('orchestrator'),
            "active_campaigns": health_check.get('active_campaigns', 0),
            "agents": health_check.get('agents', {}),
            "recommendations": [
                "All agents are healthy" if all(
                    agent.get('status') == 'healthy' 
                    for agent in health_check.get('agents', {}).values()
                ) else "Some agents may need attention",
                f"System ready for {10 - health_check.get('active_campaigns', 0)} more concurrent campaigns" if health_check.get('active_campaigns', 0) < 10 else "System at capacity"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to perform agents health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}"
        )