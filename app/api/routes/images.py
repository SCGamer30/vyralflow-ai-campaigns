from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.unsplash_service import unsplash_service
from app.models.response import APIResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/images", tags=["Images"])


@router.get("/search", response_model=APIResponse)
async def search_images(
    query: str = Query(..., description="Search query for images"),
    per_page: int = Query(6, ge=1, le=30, description="Number of images to return"),
    orientation: str = Query("landscape", description="Image orientation")
):
    """Search for images using Unsplash API."""
    try:
        logger.info(f"Searching images for query: {query}")
        
        photos = await unsplash_service.search_photos(
            query=query,
            per_page=per_page,
            orientation=orientation
        )
        
        return APIResponse(
            success=True,
            data=photos,
            message=f"Found {len(photos)} images for '{query}'"
        )
    
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search images: {str(e)}"
        )


@router.get("/curated", response_model=APIResponse)
async def get_curated_images(
    per_page: int = Query(6, ge=1, le=30, description="Number of images to return")
):
    """Get curated images from Unsplash."""
    try:
        logger.info(f"Getting {per_page} curated images")
        
        photos = await unsplash_service.get_curated_photos(per_page=per_page)
        
        return APIResponse(
            success=True,
            data=photos,
            message=f"Retrieved {len(photos)} curated images"
        )
    
    except Exception as e:
        logger.error(f"Curated images fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get curated images: {str(e)}"
        )


@router.get("/suggestions", response_model=APIResponse)
async def get_photo_suggestions(
    business_name: str = Query(..., description="Business name"),
    industry: str = Query(..., description="Industry type"),
    campaign_goal: str = Query(..., description="Campaign goal"),
    visual_themes: Optional[List[str]] = Query(None, description="Visual themes")
):
    """Get photo suggestions based on campaign context."""
    try:
        logger.info(f"Getting photo suggestions for {business_name} in {industry}")
        
        photos = await unsplash_service.get_photo_suggestions(
            business_name=business_name,
            industry=industry,
            campaign_goal=campaign_goal,
            visual_themes=visual_themes
        )
        
        return APIResponse(
            success=True,
            data=photos,
            message=f"Generated {len(photos)} photo suggestions"
        )
    
    except Exception as e:
        logger.error(f"Photo suggestions failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get photo suggestions: {str(e)}"
        )