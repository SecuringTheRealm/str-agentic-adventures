"""
Data models for the AI Dungeon Master application.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# Enum definitions
class CharacterClass(str, Enum):
    FIGHTER = "fighter"
    WIZARD = "wizard"
    ROGUE = "rogue"
    CLERIC = "cleric"
    BARD = "bard"
    DRUID = "druid"
    WARLOCK = "warlock"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    SORCERER = "sorcerer"
    BARBARIAN = "barbarian"


class Race(str, Enum):
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    DRAGONBORN = "dragonborn"
    TIEFLING = "tiefling"


class Ability(str, Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class CombatState(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    COMPLETED = "completed"


# Base models
class Abilities(BaseModel):
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10


class HitPoints(BaseModel):
    current: int
    maximum: int


class Item(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    quantity: int = 1
    weight: float | None = None
    value: int | None = None  # Value in gold pieces
    properties: dict[str, Any] | None = None


class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    TOOL = "tool"
    CONSUMABLE = "consumable"
    TREASURE = "treasure"
    RING = "ring"
    AMULET = "amulet"
    WONDROUS = "wondrous"


class Equipment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    item_type: ItemType
    rarity: ItemRarity = ItemRarity.COMMON
    weight: float | None = None
    value: int | None = None
    requires_attunement: bool = False
    is_magical: bool = False
    stat_modifiers: dict[str, int] = Field(default_factory=dict)  # e.g., {"strength": 2, "armor_class": 1}
    special_abilities: list[str] = Field(default_factory=list)
    damage_dice: str | None = None  # For weapons, e.g., "1d8"
    damage_type: str | None = None  # For weapons, e.g., "slashing"
    armor_class: int | None = None  # For armor/shields
    properties: list[str] = Field(default_factory=list)  # e.g., ["finesse", "light", "versatile"]


class EquipmentSlot(str, Enum):
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    TWO_HANDS = "two_hands"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    NECK = "neck"
    CLOAK = "cloak"


class EquippedItem(BaseModel):
    equipment_id: str
    slot: EquipmentSlot
    attuned: bool = False


class InventorySlot(BaseModel):
    item_id: str
    quantity: int
    equipped_slots: list[EquipmentSlot] = Field(default_factory=list)  # Which slots this item is equipped in


class Spell(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: str
    duration: str
    description: str
    requires_concentration: bool = False
    available_classes: list[str] = Field(default_factory=list)  # Classes that can learn this spell


class SpellSlot(BaseModel):
    level: int
    total: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)


class SpellCasting(BaseModel):
    spellcasting_ability: str  # The ability used for spellcasting (e.g., "intelligence", "wisdom", "charisma")
    spell_attack_bonus: int = 0
    spell_save_dc: int = 8
    spell_slots: list[SpellSlot] = Field(default_factory=list)
    known_spells: list[str] = Field(default_factory=list)  # Spell IDs
    prepared_spells: list[str] = Field(default_factory=list)  # Subset of known spells that are prepared
    cantrips_known: list[str] = Field(default_factory=list)  # Cantrip IDs
    concentration_spell: str | None = None  # Currently concentrating spell ID


class SpellSlotState(BaseModel):
    max_slots: dict[int, int] = Field(default_factory=dict)  # {spell_level: count}
    used_slots: dict[int, int] = Field(default_factory=dict)  # {spell_level: count}


class ConcentrationSpell(BaseModel):
    spell_id: str
    character_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_rounds: int | None = None
    save_dc: int = 10  # Base concentration DC


class CharacterSheet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    race: Race
    character_class: CharacterClass
    level: int = 1
    background: str | None = None
    alignment: str | None = None
    experience: int = 0
    abilities: Abilities
    hit_points: HitPoints
    armor_class: int = 10
    speed: int = 30
    proficiency_bonus: int = 2
    skills: dict[str, bool] = Field(default_factory=dict)
    inventory: list[InventorySlot] = Field(default_factory=list)
    equipped_items: list[EquippedItem] = Field(default_factory=list)
    carrying_capacity: float | None = None
    spells: list[Spell] = Field(default_factory=list)
    spellcasting: SpellCasting | None = None
    features: list[dict[str, Any]] = Field(default_factory=list)
    backstory: str | None = None
    # Progression tracking
    ability_score_improvements_used: int = 0
    hit_dice: str = (
        "1d8"  # Class-specific hit dice (e.g., "1d8" for rogues, "1d10" for fighters)
    )
    hit_dice_remaining: int | None = None  # Defaults to level if None
    exhaustion_level: int = 0  # 0-6, 6 = death


class CombatParticipant(BaseModel):
    id: str
    name: str
    initiative: int
    type: str  # "player" or "enemy"


class Enemy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    level: int
    hit_points: HitPoints
    initiative: int = 0
    actions: list[dict[str, Any]]
    abilities: Abilities | None = None
    armor_class: int = 10


class CombatEncounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: CombatState = CombatState.READY
    enemies: list[Enemy]
    round: int = 0
    current_turn: int | None = None
    turn_order: list[CombatParticipant] = Field(default_factory=list)
    narrative_context: dict[str, Any] = Field(default_factory=dict)


# NPC System Models
class NPCPersonality(BaseModel):
    traits: list[str] = Field(default_factory=list)  # Personality traits
    ideals: list[str] = Field(default_factory=list)  # Core beliefs
    bonds: list[str] = Field(default_factory=list)  # Important connections
    flaws: list[str] = Field(default_factory=list)  # Character flaws
    mannerisms: list[str] = Field(default_factory=list)  # Speech patterns, habits
    appearance: str | None = None
    motivations: list[str] = Field(default_factory=list)


class NPCCharacterRelationship(BaseModel):
    character_id: str
    relationship_type: str  # "friend", "enemy", "neutral", "ally", "rival"
    trust_level: int = 0  # -100 to 100
    notes: str | None = None


class NPCInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    npc_id: str
    character_id: str | None = None  # None for party interactions
    interaction_type: str  # "conversation", "combat", "trade", "quest"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str
    outcome: str | None = None
    relationship_change: int = 0  # Change in trust/reputation


class NPC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    race: str | None = None
    gender: str | None = None
    age: int | None = None
    occupation: str | None = None
    location: str | None = None
    campaign_id: str

    # Personality and behavior
    personality: NPCPersonality = NPCPersonality()
    voice_description: str | None = None

    # Game mechanics
    level: int = 1
    abilities: Abilities | None = None
    hit_points: HitPoints | None = None
    armor_class: int | None = None
    skills: dict[str, int] = Field(default_factory=dict)  # Skill bonuses

    # Relationships and interactions
    relationships: list[NPCCharacterRelationship] = Field(default_factory=list)
    interaction_history: list[str] = Field(default_factory=list)  # List of interaction IDs

    # Story relevance
    importance: str = "minor"  # "minor", "major", "critical"
    story_role: str | None = None  # "merchant", "quest_giver", "antagonist", etc.
    quest_involvement: list[str] = Field(default_factory=list)  # Quest IDs

    # Status
    is_alive: bool = True
    current_mood: str = "neutral"  # "friendly", "hostile", "neutral", "suspicious"
    notes: str | None = None


class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    setting: str
    dm_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    characters: list[str] = Field(default_factory=list)  # Character IDs
    locations: dict[str, Any] = Field(default_factory=dict)
    npcs: dict[str, Any] = Field(default_factory=dict)
    quests: dict[str, Any] = Field(default_factory=dict)
    current_location: str | None = None
    tone: str = "heroic"
    homebrew_rules: list[str] = Field(default_factory=list)
    session_log: list[dict[str, Any]] = Field(default_factory=list)
    state: str = "created"
    world_description: str | None = None
    world_art: dict[str, Any] | None = None
    is_template: bool = False
    is_custom: bool = True
    template_id: str | None = None  # For cloned campaigns
    plot_hooks: list[str] = Field(default_factory=list)
    key_npcs: list[str] = Field(default_factory=list)


# Request/Response models
class CreateCharacterRequest(BaseModel):
    name: str = Field(max_length=100)
    race: Race
    character_class: CharacterClass
    abilities: Abilities
    backstory: str | None = Field(default=None, max_length=2000)
    background: str | None = Field(
        default=None, max_length=100
    )  # Background choice from SRD (acolyte, criminal, etc.)


class LevelUpRequest(BaseModel):
    character_id: str
    ability_improvements: dict[str, int] | None = (
        None  # {"strength": 1, "dexterity": 1} for +2 ASI
    )
    feat_choice: str | None = None  # Name of feat if chosen instead of ASI


class LevelUpResponse(BaseModel):
    success: bool
    new_level: int
    hit_points_gained: int
    ability_improvements: dict[str, int]
    new_proficiency_bonus: int
    features_gained: list[str]
    message: str


class PlayerInput(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    character_id: str = Field(min_length=1, max_length=100)
    campaign_id: str = Field(min_length=1, max_length=100)


class GameResponse(BaseModel):
    message: str
    images: list[str] = Field(default_factory=list)
    state_updates: dict[str, Any] = Field(default_factory=dict)
    combat_updates: dict[str, Any] | None = None


class CreateCampaignRequest(BaseModel):
    name: str = Field(max_length=200)
    setting: str = Field(max_length=1000)
    tone: str | None = Field(default="heroic", max_length=100)
    homebrew_rules: list[str] | None = Field(default_factory=list)
    description: str | None = Field(default=None, max_length=2000)


class CampaignUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    setting: str | None = None
    tone: str | None = None
    homebrew_rules: list[str] | None = None
    world_description: str | None = None


class CloneCampaignRequest(BaseModel):
    template_id: str
    new_name: str | None = None


class CampaignListResponse(BaseModel):
    campaigns: list[Campaign]
    templates: list[Campaign]


class AIAssistanceRequest(BaseModel):
    text: str = Field(max_length=2000)
    context_type: str = Field(max_length=100)  # "setting", "description", "plot_hook", etc.
    campaign_tone: str | None = Field(default="heroic", max_length=100)


class AIAssistanceResponse(BaseModel):
    suggestions: list[str]
    enhanced_text: str | None = None


class AIContentGenerationRequest(BaseModel):
    suggestion: str = Field(max_length=1000)  # The specific suggestion to generate content for
    current_text: str = Field(max_length=2000)  # Current text in the field
    context_type: str = Field(max_length=100)  # "setting", "description", "plot_hook", etc.
    campaign_tone: str | None = Field(default="heroic", max_length=100)


class AIContentGenerationResponse(BaseModel):
    generated_content: str
    success: bool
    error: str | None = None


class GenerateImageRequest(BaseModel):
    image_type: str  # "character_portrait", "scene_illustration", "item_visualization"
    details: dict[str, Any]


class BattleMapRequest(BaseModel):
    environment: dict[str, Any]
    combat_context: dict[str, Any] | None = None


# Narrative Generation Models
class NarrativeChoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    description: str | None = None
    consequences: dict[str, Any] = Field(default_factory=dict)
    requirements: dict[str, Any] = Field(default_factory=dict)  # Conditions that must be met to show this choice
    weight: float = 1.0  # Probability weight for random selection


class PlotPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: str  # "introduction", "conflict", "climax", "resolution", "subplot"
    status: str = "pending"  # "pending", "active", "completed", "skipped"
    dependencies: list[str] = Field(default_factory=list)  # IDs of plot points that must be completed first
    triggers: dict[str, Any] = Field(default_factory=dict)  # Conditions that activate this plot point
    outcomes: dict[str, Any] = Field(default_factory=dict)  # Results when this plot point is completed
    importance: int = 5  # 1-10 scale
    estimated_duration: int | None = None  # Expected number of scenes/sessions


class StoryArc(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: str  # "main", "side", "character", "world"
    status: str = "planning"  # "planning", "active", "paused", "completed"
    plot_points: list[str] = Field(default_factory=list)  # PlotPoint IDs in order
    current_point: str | None = None  # Current active plot point ID
    characters_involved: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    estimated_length: int | None = None  # Expected number of sessions
    player_choices: list[str] = Field(default_factory=list)  # NarrativeChoice IDs that influenced this arc


class NarrativeState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    current_scene: str | None = None
    active_story_arcs: list[str] = Field(default_factory=list)  # StoryArc IDs
    completed_story_arcs: list[str] = Field(default_factory=list)  # StoryArc IDs
    pending_choices: list[str] = Field(default_factory=list)  # NarrativeChoice IDs available to players
    narrative_flags: dict[str, Any] = Field(default_factory=dict)  # Story flags and variables
    character_relationships: dict[
        str, dict[str, Any]
    ] = Field(default_factory=dict)  # Character interaction history
    world_state: dict[str, Any] = Field(default_factory=dict)  # Current state of locations, factions, etc.
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NarrativeEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: str  # "choice_made", "plot_point_completed", "character_interaction", "world_change"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    characters_involved: list[str] = Field(default_factory=list)
    location: str | None = None
    choices_made: list[str] = Field(default_factory=list)  # NarrativeChoice IDs
    consequences: dict[str, Any] = Field(default_factory=dict)
    story_arc_id: str | None = None
    plot_point_id: str | None = None


class SpellAttackBonusRequest(BaseModel):
    character_class: CharacterClass
    level: int
    spellcasting_ability_score: int


# Spell-related request and response models
class ManageSpellsRequest(BaseModel):
    character_id: str
    action: Literal["learn", "forget", "prepare", "unprepare"]
    spell_ids: list[str]


class ManageSpellSlotsRequest(BaseModel):
    character_id: str
    action: Literal["use", "recover", "set"]
    slot_level: int
    count: int | None = 1


class CastSpellRequest(BaseModel):
    combat_id: str
    character_id: str
    spell_id: str
    slot_level: int
    target_ids: list[str] | None = Field(default_factory=list)
    spell_attack_roll: int | None = None


class SpellListRequest(BaseModel):
    character_class: CharacterClass | None = None
    spell_level: int | None = None
    school: str | None = None


class ConcentrationRequest(BaseModel):
    character_id: str
    action: Literal["start", "end", "check"]
    spell_id: str | None = None
    damage_taken: int | None = None


class SpellListResponse(BaseModel):
    spells: list[Spell]
    total_count: int


class SpellCastingResponse(BaseModel):
    success: bool
    message: str
    spell_effects: dict[str, Any] = Field(default_factory=dict)
    concentration_broken: bool = False
    slot_used: bool = False


class ConcentrationCheckResponse(BaseModel):
    success: bool
    concentration_maintained: bool
    dc: int
    roll_result: int | None = None
    spell_ended: bool = False


# Inventory-related request and response models
class ManageEquipmentRequest(BaseModel):
    character_id: str
    action: Literal["equip", "unequip"]
    equipment_id: str
    slot: EquipmentSlot | None = None


class EncumbranceRequest(BaseModel):
    character_id: str


class MagicalEffectsRequest(BaseModel):
    character_id: str
    item_id: str
    action: Literal["apply", "remove"]


class ItemCatalogRequest(BaseModel):
    item_type: ItemType | None = None
    rarity: ItemRarity | None = None
    min_value: int | None = None
    max_value: int | None = None


class EquipmentResponse(BaseModel):
    success: bool
    message: str
    stat_changes: dict[str, int] = Field(default_factory=dict)
    armor_class_change: int | None = None


class EncumbranceResponse(BaseModel):
    character_id: str
    current_weight: float
    carrying_capacity: float
    encumbrance_level: str  # "unencumbered", "encumbered", "heavily_encumbered"
    speed_penalty: int = 0


class ItemCatalogResponse(BaseModel):
    items: list[Equipment]
    total_count: int


class MagicalEffectsResponse(BaseModel):
    success: bool
    message: str
    active_effects: list[str]
    stat_modifiers: dict[str, int]


# NPC-related request and response models
class CreateNPCRequest(BaseModel):
    campaign_id: str
    name: str
    race: str | None = None
    gender: str | None = None
    age: int | None = None
    occupation: str | None = None
    location: str | None = None
    importance: str = "minor"
    story_role: str | None = None


class UpdateNPCRequest(BaseModel):
    name: str | None = None
    occupation: str | None = None
    location: str | None = None
    current_mood: str | None = None
    notes: str | None = None


class NPCInteractionRequest(BaseModel):
    npc_id: str
    character_id: str | None = None
    interaction_type: str = Field(max_length=100)
    summary: str = Field(max_length=2000)
    outcome: str | None = Field(default=None, max_length=1000)
    relationship_change: int = 0


class GenerateNPCStatsRequest(BaseModel):
    npc_id: str
    level: int | None = None
    role: str = "civilian"  # "civilian", "guard", "soldier", "spellcaster", "rogue"


class NPCPersonalityRequest(BaseModel):
    npc_id: str


class NPCListResponse(BaseModel):
    npcs: list[NPC]
    total_count: int


class NPCInteractionResponse(BaseModel):
    success: bool
    message: str
    interaction_id: str
    new_relationship_level: int | None = None


class NPCStatsResponse(BaseModel):
    success: bool
    message: str
    generated_stats: dict[str, Any]


# ---------------------------------------------------------------------------
# Save Slot models
# ---------------------------------------------------------------------------

MAX_SAVE_SLOTS = 5


class SaveSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    slot_number: int  # 1-5
    name: str = ""  # user-provided label
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    play_time_seconds: int = 0
    interaction_count: int = 0
    character_level: int = 1
    current_location: str = ""
    save_data: dict[str, Any] = Field(default_factory=dict)  # full state blob


class CreateSaveSlotRequest(BaseModel):
    name: str = Field(default="", max_length=200)
    play_time_seconds: int = Field(default=0, ge=0)
    interaction_count: int = Field(default=0, ge=0)
    character_level: int = Field(default=1, ge=1, le=20)
    current_location: str = Field(default="", max_length=500)
    save_data: dict[str, Any] = Field(default_factory=dict)


class SaveSlotListResponse(BaseModel):
    saves: list[SaveSlot]
    total_count: int


# NPC Profile models for game-engine disposition tracking


class NPCConversationEntry(BaseModel):
    """A single recorded conversation with an NPC."""

    timestamp: str
    summary: str
    disposition_change: int = 0
    topics: list[str] = Field(default_factory=list)


class NPCProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    personality_traits: list[str] = Field(default_factory=list)
    disposition: Literal["friendly", "neutral", "hostile", "fearful"] = "neutral"
    location: str = ""
    is_alive: bool = True
    conversation_notes: list[str] = Field(default_factory=list)
    conversation_history: list[NPCConversationEntry] = Field(default_factory=list)


class NPCRelationship(BaseModel):
    npc_id: str
    campaign_id: str
    disposition_score: int = 0  # -100 to 100
    interactions_count: int = 0
    key_events: list[str] = Field(default_factory=list)
    last_interaction: str = ""


class CreateNPCProfileRequest(BaseModel):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    personality_traits: list[str] = Field(default_factory=list)
    disposition: Literal["friendly", "neutral", "hostile", "fearful"] = "neutral"
    location: str = Field(default="", max_length=500)


class UpdateDispositionRequest(BaseModel):
    disposition_score: int
    event_note: str | None = Field(default=None, max_length=500)


class RecordConversationRequest(BaseModel):
    """Request body for recording an NPC conversation."""

    summary: str = Field(max_length=2000)
    disposition_change: int = 0
    topics: list[str] = Field(default_factory=list)


class NPCProfileWithRelationship(BaseModel):
    profile: NPCProfile
    relationship: NPCRelationship | None = None


class NPCProfileListResponse(BaseModel):
    npcs: list[NPCProfile]
    total_count: int


class RestType(str, Enum):
    SHORT = "short"
    LONG = "long"


class RestRequest(BaseModel):
    character_id: str
    rest_type: RestType
    hit_dice_to_spend: int = 0


class RestResponse(BaseModel):
    success: bool
    message: str
    hp_recovered: int = 0
    spell_slots_recovered: list[int] = Field(default_factory=list)
    hit_dice_remaining: int = 0
    exhaustion_level: int = 0
