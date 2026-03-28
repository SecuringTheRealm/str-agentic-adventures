"""AI generation endpoint routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.agents.artist_agent import get_artist
from app.agents.combat_cartographer_agent import get_combat_cartographer
from app.api.routes._shared import _get_image_budget, limiter
from app.models.game_models import (
    AIAssistanceRequest,
    AIAssistanceResponse,
    AIContentGenerationRequest,
    AIContentGenerationResponse,
    GenerateImageRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


@router.post("/campaign/ai-assist", response_model=AIAssistanceResponse)
async def get_ai_assistance(request: AIAssistanceRequest) -> dict[str, Any]:
    """Get AI assistance for campaign text enhancement."""
    try:
        # For now, provide simple suggestions based on context type
        # In a full implementation, this would use the AI agents
        suggestions = []
        enhanced_text = None

        if request.context_type == "setting":
            suggestions = [
                "Add more sensory details (sights, sounds, smells)",
                "Include potential conflict sources or tensions",
                "Describe the political or social climate",
                "Mention notable landmarks or geographical features",
            ]
        elif request.context_type == "description":
            suggestions = [
                "Expand on character motivations",
                "Add more dialogue or character interactions",
                "Include environmental details that set the mood",
                "Consider adding a plot twist or complication",
            ]
        elif request.context_type == "plot_hook":
            suggestions = [
                "Make the stakes more personal for the characters",
                "Add a time pressure element",
                "Include moral dilemmas or difficult choices",
                "Connect to character backstories",
            ]
        else:
            suggestions = [
                "Consider your target audience and tone",
                "Add specific details that engage the senses",
                "Think about cause and effect relationships",
                "Ensure consistency with your campaign world",
            ]

        # Simple text enhancement - in a full implementation this would use AI
        enhanced_text = None
        if request.text:
            # Basic text enhancement with context-aware improvements
            text = request.text.strip()

            if request.context_type == "setting":
                # Add atmospheric details for settings
                enhanced_text = f"{text}\n\nThe air carries subtle hints of the environment's character, while distant sounds suggest the life and activity that defines this place."
            elif request.context_type == "description":
                # Add depth to descriptions
                enhanced_text = f"{text}\n\nBeneath the surface details lies a sense of deeper significance, as if each element serves a purpose in the larger tapestry of the story."
            elif request.context_type == "plot_hook":
                # Add urgency to plot hooks
                enhanced_text = f"{text}\n\nTime seems to be of the essence, and the consequences of action—or inaction—weigh heavily on the minds of those involved."
            else:
                # General enhancement
                enhanced_text = f"{text}\n\nThis element resonates with potential, offering opportunities for creative development and meaningful narrative engagement."

        return AIAssistanceResponse(
            suggestions=suggestions, enhanced_text=enhanced_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI assistance: {str(e)}",
        ) from e


@router.post("/campaign/ai-generate", response_model=AIContentGenerationResponse)
@limiter.limit("30/minute")
async def generate_ai_content(  # noqa: ARG001
    request: Request,
    request_body: AIContentGenerationRequest,
) -> AIContentGenerationResponse:
    """Generate AI content based on a specific suggestion and current text."""
    try:
        from app.azure_openai_client import azure_openai_client

        # Create contextual prompt - user input goes in user message only
        system_prompt = (
            "You are an expert D&D campaign writer helping to enhance campaign content.\n"
            "Your task is to generate creative, contextual content based on a specific suggestion.\n\n"
            "Guidelines:\n"
            "- Generate 2-4 sentences of high-quality content that fulfills the suggestion\n"
            "- If there's existing text, build upon it naturally and coherently\n"
            "- Match the campaign tone specified by the user\n"
            "- Be specific and evocative, not generic\n"
            "- Focus on details that enhance the game experience\n"
            "- Don't repeat the suggestion text itself\n\n"
            "Respond with ONLY the generated content, no explanations or meta-text."
        )

        user_prompt = (
            f"Campaign Tone: {request_body.campaign_tone}\n"
            f"Context Type: {request_body.context_type}\n"
            f"Current field content: {request_body.current_text or '(empty)'}\n\n"
            f"Suggestion to implement: {request_body.suggestion}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Generate content using Azure OpenAI
        generated_content = await azure_openai_client.chat_completion(
            messages, temperature=0.7, max_tokens=300
        )

        if not generated_content or generated_content.strip() == "":
            return AIContentGenerationResponse(
                generated_content="", success=False, error="Failed to generate content"
            )

        return AIContentGenerationResponse(
            generated_content=generated_content.strip(), success=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI content: {str(e)}",
        ) from e


@router.post("/generate-image", response_model=dict[str, Any])
@limiter.limit("5/minute")
async def generate_image(  # noqa: ARG001
    request: Request, image_request: GenerateImageRequest,
) -> dict[str, Any]:
    """Generate an image based on the request details.

    Accepts an optional ``session_id`` field in the request body.  Each session
    is limited to ``max_images_per_session`` DALL-E calls per rolling
    ``image_session_window_minutes`` window (configurable via environment
    variables).  Requests that exceed the budget receive a 429 response.
    """
    try:
        # Enforce per-session image budget
        session_id = str(image_request.session_id or "anonymous")
        budget = _get_image_budget()
        allowed, remaining = budget.check_and_record(session_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Image budget exceeded. You may generate at most "
                    f"{budget.max_images} image(s) per "
                    f"{budget.window.seconds // 60}-minute session."
                ),
            )

        image_type = image_request.image_type
        details = image_request.details

        if image_type == "character_portrait":
            result = await get_artist().generate_character_portrait(details)
        elif image_type == "scene_illustration":
            result = await get_artist().illustrate_scene(details)
        elif image_type == "item_visualization":
            result = await get_artist().create_item_visualization(details)

        result["images_remaining"] = remaining
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}",
        ) from e


@router.post("/battle-map", response_model=dict[str, Any])
@limiter.limit("5/minute")
async def generate_battle_map(  # noqa: ARG001
    request: Request, map_request: dict[str, Any],
) -> dict[str, Any]:
    """Generate a battle map based on environment details.

    Accepts an optional ``session_id`` field in the request body.  The same
    per-session image budget used by ``/generate-image`` applies here.
    """
    try:
        # Enforce per-session image budget (battle maps count as images)
        session_id = str(map_request.get("session_id") or "anonymous")
        budget = _get_image_budget()
        allowed, remaining = budget.check_and_record(session_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Image budget exceeded. You may generate at most "
                    f"{budget.max_images} image(s) per "
                    f"{budget.window.seconds // 60}-minute session."
                ),
            )

        environment = map_request.get("environment", {})
        combat_context = map_request.get("combat_context")

        result = await get_combat_cartographer().generate_battle_map(
            environment, combat_context
        )
        result["images_remaining"] = remaining
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}",
        ) from e
