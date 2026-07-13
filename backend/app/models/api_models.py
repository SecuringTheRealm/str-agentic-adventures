"""Response models for API routes that previously returned bare dicts.

These mirror the actual dict shapes built in ``app.api.routes.*`` and the
services/agents those routes call (see the route function for the exact
construction). Grouped by the route module that uses each model. Where a
route's return shape is genuinely polymorphic (dice notation parsing, AI
image generation results), the model declares the common fields and allows
extras through rather than silently dropping data.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.game_models import Abilities, Campaign, CharacterSheet, HitPoints

# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# ai_routes.py
# ---------------------------------------------------------------------------


class ImageGenerationStatusResponse(BaseModel):
    available: bool
    status: str
    message: str | None = None


class GeneratedImageResult(BaseModel):
    """Shape returned by POST /generate-image.

    The artist agent returns different optional fields depending on image
    type (character_portrait/scene_illustration/item_visualization) and
    whether generation succeeded or fell back to a placeholder; unlisted
    fields pass through unchanged.
    """

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    type: str | None = None
    description: str | None = None
    image_url: str | None = None
    revised_prompt: str | None = None
    placeholder: bool | None = None
    error: str | None = None
    generation_details: dict[str, Any] | None = None
    images_remaining: int | None = None


class BattleMapResult(BaseModel):
    """Shape returned by POST /battle-map.

    Either the artist-generated battle map dict, or (when Azure OpenAI is
    unavailable) a BattleMapData grid dump -- the two shapes barely
    overlap, so unlisted fields pass through unchanged.
    """

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    error: str | None = None
    images_remaining: int | None = None


# ---------------------------------------------------------------------------
# campaign_routes.py
# ---------------------------------------------------------------------------


class CampaignTemplatesResponse(BaseModel):
    templates: list[Campaign]


# ---------------------------------------------------------------------------
# character_routes.py
# ---------------------------------------------------------------------------


class CharacterGetResponse(CharacterSheet):
    """GET /character/{id} response.

    Same shape as CharacterSheet, but abilities/hit_points are optional:
    persisted character records aren't schema-validated on write, so a
    partial record (e.g. one created before those fields existed) is a
    valid 200 response, not a 500.
    """

    abilities: Abilities | None = None
    hit_points: HitPoints | None = None


class LevelUpResult(BaseModel):
    success: bool
    character_id: str
    old_level: int
    new_level: int
    hit_points_gained: int
    ability_improvements: dict[str, int]
    new_proficiency_bonus: int
    features_gained: list[str]
    hp_calculation: dict[str, Any]
    updated_character: dict[str, Any]


class AwardExperienceResult(BaseModel):
    character_id: str
    experience_awarded: int
    old_experience: int
    new_experience: int
    level_info: dict[str, Any]
    can_level_up: bool


class ProgressionInfoResponse(BaseModel):
    character_id: str
    current_level: int
    level_info: dict[str, Any]
    asi_info: dict[str, Any]
    proficiency_info: dict[str, Any]


# ---------------------------------------------------------------------------
# combat_routes.py
# ---------------------------------------------------------------------------


class CombatInitResult(BaseModel):
    combat_id: str
    session_id: str
    status: str
    round: int
    current_turn: int
    initiative_order: list[dict[str, Any]]
    environment: str
    battle_map_requested: bool
    started_at: str


class CombatTurnResult(BaseModel):
    combat_id: str
    character_id: str | None = None
    action: str
    target_id: str | None = None
    success: bool
    damage: int
    description: str
    next_turn: bool
    timestamp: str
    attack_roll: dict[str, Any] | None = None
    damage_roll: dict[str, Any] | None = None
    stealth_roll: dict[str, Any] | None = None
    action_economy: dict[str, bool] | None = None
    """Acting combatant's action/bonus_action/reaction used-flags after this turn (#769)."""


class EncounterGenerationResult(BaseModel):
    monsters: list[dict[str, Any]]
    difficulty: str
    xp_budget: int
    adjusted_xp: int
    raw_xp: int
    xp_per_character: int
    party_size: int


class XPAwardResult(BaseModel):
    total_xp: int
    xp_per_character: int
    party_size: int


# ---------------------------------------------------------------------------
# dice_routes.py
# ---------------------------------------------------------------------------


class DiceRollResult(BaseModel):
    """Shape returned by the dice roller / rules engine.

    Notation supports single pools, multi-pool expressions, rerolls, and
    keep/drop modifiers, each of which adds different optional keys
    (pools, rerolls, dropped, character_bonus, ...); unlisted fields pass
    through unchanged rather than being silently dropped.
    """

    model_config = ConfigDict(extra="allow")

    notation: str
    total: int
    rolls: list[int] | None = None
    modifier: int | None = None


# ---------------------------------------------------------------------------
# npc_routes.py
# ---------------------------------------------------------------------------


class NPCDialogueContextResponse(BaseModel):
    name: str
    description: str
    personality_traits: list[str]
    disposition: str
    disposition_score: int
    disposition_tone: str
    location: str
    is_alive: bool
    conversation_notes: list[str]
    recent_conversations: list[dict[str, Any]]
    interactions_count: int
    key_events: list[str]


class NPCConversationRecordedResponse(BaseModel):
    status: str
    npc_id: str
    campaign_id: str


# ---------------------------------------------------------------------------
# realtime.py
# ---------------------------------------------------------------------------


class RealtimeTokenResponse(BaseModel):
    token: str
    endpoint: str
    deployment: str
    voice: str
    expires_at: int | None = None


# ---------------------------------------------------------------------------
# save_routes.py
# ---------------------------------------------------------------------------


class SaveSlotLoadResponse(BaseModel):
    slot_number: int
    name: str
    character_level: int
    current_location: str
    play_time_seconds: int
    interaction_count: int
    save_data: dict[str, Any]


class SaveSlotRestoreResponse(BaseModel):
    status: str
    slot_number: int
    name: str
    restored_summary: dict[str, Any]


class SaveSlotSummaryResponse(BaseModel):
    campaign_name: str
    setting: str
    current_location: str
    characters: list[str]
    character_count: int
    npc_count: int
    npc_names: list[str]
    conversation_entries: int
    has_active_combat: bool
    captured_at: str
    version: int


# ---------------------------------------------------------------------------
# session_routes.py
# ---------------------------------------------------------------------------


class WorldLocation(BaseModel):
    name: str
    type: str
    description: str


class WorldNPC(BaseModel):
    name: str
    role: str
    description: str


class GeneratedWorldElements(BaseModel):
    major_locations: list[WorldLocation]
    notable_npcs: list[WorldNPC]
    plot_hooks: list[str]
    world_lore: list[str]


class CampaignWorldGenerationResponse(BaseModel):
    world_description: str
    setting: str
    tone: str
    generated_elements: GeneratedWorldElements


class GameSessionStartResponse(BaseModel):
    id: str
    campaign_id: str
    status: str
    created_at: str | None = None
    turn_order: list[str] = Field(default_factory=list)
    current_turn_index: int = 0
    type: str
    character_ids: list[str]
    current_scene: str
    available_actions: list[str]
    scene_count: int


class OpeningNarrativeResponse(BaseModel):
    scene_description: str
    quest_hook: str
    suggested_actions: list[str]
    help_text: str


class PlayerActionResult(BaseModel):
    """Shape returned by POST /session/{session_id}/action.

    Fields present vary by action type (combat/skill_check/exploration/
    general); type-specific fields are optional.
    """

    type: str
    description: str
    result: str
    session_id: str
    timestamp: str
    next_actions: list[str]
    success: bool | None = None
    damage: int | None = None
    dice_rolls: list[dict[str, Any]] | None = None
    effects: list[str] | None = None
    perception_roll: dict[str, Any] | None = None
    discoveries: list[str] | None = None
    specialist_results: dict[str, Any] | None = None


class SessionParticipantResponse(BaseModel):
    id: str
    session_id: str
    character_id: str
    player_name: str
    is_dm: bool
    is_connected: bool
    joined_at: str | None = None


class MultiplayerSessionResponse(BaseModel):
    id: str
    campaign_id: str
    status: str
    created_at: str | None = None
    turn_order: list[str] = Field(default_factory=list)
    current_turn_index: int = 0
    participants: list[SessionParticipantResponse] | None = None


class TurnAdvanceResponse(BaseModel):
    character_id: str
    player_name: str


# ---------------------------------------------------------------------------
# spell_routes.py
# ---------------------------------------------------------------------------


class ManageSpellsResult(BaseModel):
    character_id: str
    action: str
    spell_ids: list[str]
    success: bool
    message: str


class ManageSpellSlotsResult(BaseModel):
    character_id: str
    action: str
    slot_level: int
    count: int | None
    success: bool
    message: str


class SpellSaveDCResponse(BaseModel):
    save_dc: int
    character_class: str
    level: int
    spellcasting_ability: str
    spellcasting_ability_score: int
    ability_modifier: int
    proficiency_bonus: int


class SpellAttackBonusResponse(BaseModel):
    character_class: str
    level: int
    spellcasting_ability: str
    spellcasting_ability_score: int
    ability_modifier: int
    proficiency_bonus: int
    spell_attack_bonus: int
