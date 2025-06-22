from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List

from app.models.campaign import (
    CampaignRequest, CampaignResponse, CampaignStatus, 
    CampaignResults, CampaignListResponse, CampaignStatusResponse
)
from app.models.response import APIResponse, ErrorResponse
from app.core.orchestrator import campaign_orchestrator
from app.core.exceptions import CampaignNotFoundException, AgentExecutionException
from app.api.dependencies import (
    get_orchestrator, validate_campaign_id, rate_limiter, 
    get_current_user, log_request
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/create", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_request: CampaignRequest,
    orchestrator = Depends(get_orchestrator),
    _rate_limit = Depends(rate_limiter),
    _user = Depends(get_current_user),
    _log = Depends(log_request)
):
    """
    Create a new viral social media campaign.
    
    This endpoint creates a new campaign and starts the AI agent workflow.
    The agents will execute in sequence: Trend Analyzer → Content Writer → Visual Designer → Campaign Scheduler.
    
    **Request Body:**
    - **business_name**: Name of your business or brand
    - **industry**: Your business industry (e.g., "food & beverage", "technology")
    - **campaign_goal**: Main objective of the campaign
    - **target_platforms**: List of social media platforms to target
    - **brand_voice**: Tone and style for content (optional, defaults to "professional")
    - **target_audience**: Description of your target audience (optional)
    - **keywords**: Relevant keywords for the campaign (optional)
    
    **Response:**
    Returns the campaign ID and initial status. Use the status endpoint to track progress.
    """
    try:
        logger.info(f"Creating campaign for {campaign_request.business_name}")
        
        # Create and start campaign
        campaign_response = await orchestrator.create_campaign(campaign_request)
        
        logger.info(f"Campaign created successfully: {campaign_response.campaign_id}")
        return campaign_response
        
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/{campaign_id}/status", response_model=CampaignResponse)
async def get_campaign_status(
    campaign_id: str = Depends(validate_campaign_id),
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    Get the current status of a campaign.
    
    Returns detailed information about the campaign including:
    - Current status (processing, completed, failed)
    - Progress of each AI agent
    - Any error messages if the campaign failed
    
    **Path Parameters:**
    - **campaign_id**: The unique campaign identifier
    
    **Response:**
    - **campaign_id**: Campaign identifier
    - **status**: Current campaign status
    - **agent_progress**: Array of agent progress information
    - **results**: Campaign results (only when completed)
    - **created_at**: Campaign creation timestamp
    - **completed_at**: Campaign completion timestamp (if completed)
    """
    try:
        campaign_response = await orchestrator.get_campaign_status(campaign_id)
        return campaign_response
        
    except CampaignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found"
        )
    except Exception as e:
        logger.error(f"Failed to get campaign status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign status: {str(e)}"
        )


@router.get("/{campaign_id}/results", response_model=CampaignResults)
async def get_campaign_results(
    campaign_id: str = Depends(validate_campaign_id),
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    Get the complete results of a completed campaign.
    
    This endpoint returns all results from the AI agents:
    - **Trend Analysis**: Trending topics, hashtags, and analysis summary
    - **Content**: Platform-specific content with variations
    - **Visual Design**: Image suggestions, color palettes, and style recommendations
    - **Scheduling**: Optimal posting times and coordinated posting sequence
    
    **Path Parameters:**
    - **campaign_id**: The unique campaign identifier
    
    **Response:**
    Complete campaign results including all agent outputs.
    
    **Note:** This endpoint only returns data for completed campaigns.
    """
    try:
        campaign_results = await orchestrator.get_campaign_results(campaign_id)
        return campaign_results
        
    except CampaignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found"
        )
    except AgentExecutionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get campaign results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign results: {str(e)}"
        )


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    status_filter: Optional[CampaignStatus] = Query(None, alias="status", description="Filter by campaign status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    List campaigns with optional filtering and pagination.
    
    **Query Parameters:**
    - **status**: Filter campaigns by status (pending, processing, completed, failed)
    - **limit**: Maximum number of campaigns to return (1-100, default: 10)
    - **offset**: Number of campaigns to skip for pagination (default: 0)
    
    **Response:**
    Array of campaign objects with basic information and current status.
    """
    try:
        campaigns = await orchestrator.list_campaigns(
            status=status_filter,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Listed {len(campaigns)} campaigns")
        return campaigns
        
    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}"
        )


@router.delete("/{campaign_id}/cancel", response_model=APIResponse)
async def cancel_campaign(
    campaign_id: str = Depends(validate_campaign_id),
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    Cancel an active campaign.
    
    This endpoint attempts to cancel a campaign that is currently processing.
    It will stop the current agent execution and mark the campaign as failed.
    
    **Path Parameters:**
    - **campaign_id**: The unique campaign identifier
    
    **Response:**
    Success or failure message.
    
    **Note:** Only active/processing campaigns can be cancelled.
    """
    try:
        success = await orchestrator.cancel_campaign(campaign_id)
        
        if success:
            logger.info(f"Campaign {campaign_id} cancelled successfully")
            return APIResponse(
                success=True,
                message=f"Campaign {campaign_id} cancelled successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campaign {campaign_id} cannot be cancelled (not active or already completed)"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel campaign: {str(e)}"
        )


@router.get("/active", response_model=List[str])
async def get_active_campaigns(
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    Get list of currently active campaign IDs.
    
    Returns a list of campaign IDs that are currently being processed by the AI agents.
    
    **Response:**
    Array of active campaign IDs.
    """
    try:
        active_campaigns = await orchestrator.get_active_campaigns()
        return active_campaigns
        
    except Exception as e:
        logger.error(f"Failed to get active campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active campaigns: {str(e)}"
        )


@router.get("/{campaign_id}/quick-status")
async def get_quick_campaign_status(
    campaign_id: str = Depends(validate_campaign_id),
    orchestrator = Depends(get_orchestrator),
    _user = Depends(get_current_user)
):
    """
    Get quick status summary of a campaign (optimized for frequent polling).
    
    This is a lightweight endpoint optimized for real-time status updates.
    Returns minimal information suitable for progress indicators.
    
    **Path Parameters:**
    - **campaign_id**: The unique campaign identifier
    
    **Response:**
    Lightweight status information including current progress and agent status.
    """
    try:
        campaign_response = await orchestrator.get_campaign_status(campaign_id)
        
        # Extract quick status information
        overall_progress = 0
        current_agent = None
        
        if campaign_response.agent_progress:
            completed_agents = sum(1 for agent in campaign_response.agent_progress if agent.status == "completed")
            total_agents = len(campaign_response.agent_progress)
            overall_progress = int((completed_agents / total_agents) * 100)
            
            # Find current running agent
            for agent in campaign_response.agent_progress:
                if agent.status == "running":
                    current_agent = agent.agent_name
                    break
        
        return {
            "campaign_id": campaign_id,
            "status": campaign_response.status.value,
            "overall_progress": overall_progress,
            "current_agent": current_agent,
            "is_completed": campaign_response.status == CampaignStatus.COMPLETED,
            "has_error": campaign_response.status == CampaignStatus.FAILED,
            "error_message": campaign_response.error_message
        }
        
    except CampaignNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found"
        )
    except Exception as e:
        logger.error(f"Failed to get quick campaign status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quick campaign status: {str(e)}"
        )