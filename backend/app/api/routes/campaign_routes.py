"""Campaign CRUD routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.config import ConfigDep
from app.models.game_models import (
    Campaign,
    CampaignListResponse,
    CampaignUpdateRequest,
    CloneCampaignRequest,
    CreateCampaignRequest,
)
from app.services.campaign_service import campaign_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])


@router.post("/campaign", response_model=Campaign)
async def create_campaign(campaign_data: CreateCampaignRequest, config: ConfigDep) -> dict[str, Any]:
    """Create a new campaign."""
    try:
        # Campaign creation doesn't require Azure OpenAI - it's just database operations
        return campaign_service.create_campaign(campaign_data)
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except ValueError as e:
        # Handle configuration errors specifically
        error_msg = str(e)
        if "Azure OpenAI configuration" in error_msg:
            logger.exception("Configuration error during campaign creation")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_msg
            ) from None
        logger.exception("Validation error during campaign creation")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except Exception as e:
        logger.exception("Unexpected error during campaign creation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        ) from None


@router.get("/campaigns", response_model=CampaignListResponse)
async def list_campaigns() -> dict[str, Any]:
    """List all campaigns including templates and custom campaigns."""
    try:
        all_campaigns = campaign_service.list_campaigns()
        templates = campaign_service.get_templates()

        return CampaignListResponse(campaigns=all_campaigns, templates=templates)
    except Exception as e:
        logger.exception("Error listing campaigns")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        ) from e


@router.get("/campaign/templates")
async def get_campaign_templates() -> dict[str, Any]:
    """Get pre-built campaign templates."""
    try:
        templates = campaign_service.get_templates()
        return {"templates": templates}
    except Exception as e:
        logger.exception("Error getting campaign templates")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}",
        ) from None


@router.get("/campaign/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str) -> dict[str, Any]:
    """Get a specific campaign by ID."""
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found",
            ) from None
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}",
        ) from None


@router.put("/campaign/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, updates: CampaignUpdateRequest) -> dict[str, Any]:
    """Update an existing campaign."""
    try:
        # Convert to dict, excluding None values
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid updates provided",
            ) from None

        updated_campaign = campaign_service.update_campaign(campaign_id, update_data)
        if not updated_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found",
            )

        return updated_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        ) from None


@router.post("/campaign/clone", response_model=Campaign)
async def clone_campaign(clone_data: CloneCampaignRequest) -> dict[str, Any]:
    """Clone a template campaign for customization."""
    try:
        cloned_campaign = campaign_service.clone_campaign(
            clone_data.template_id, clone_data.new_name
        )

        if not cloned_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template campaign {clone_data.template_id} not found",
            )

        return cloned_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone campaign: {str(e)}",
        ) from None


@router.delete("/campaign/{campaign_id}")
async def delete_campaign(campaign_id: str) -> dict[str, Any]:
    """Delete a custom campaign (templates cannot be deleted)."""
    try:
        success = campaign_service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found or cannot be deleted",
            ) from None

        return {"message": "Campaign deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}",
        ) from None
