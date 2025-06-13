"""
Data models for the AI Dungeon Master application.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid

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
    description: Optional[str] = None
    quantity: int = 1
    weight: Optional[float] = None
    value: Optional[int] = None  # Value in gold pieces
    properties: Optional[Dict[str, Any]] = None

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
    description: Optional[str] = None
    item_type: ItemType
    rarity: ItemRarity = ItemRarity.COMMON
    weight: Optional[float] = None
    value: Optional[int] = None
    requires_attunement: bool = False
    is_magical: bool = False
    stat_modifiers: Dict[str, int] = {}  # e.g., {"strength": 2, "armor_class": 1}
    special_abilities: List[str] = []
    damage_dice: Optional[str] = None  # For weapons, e.g., "1d8"
    damage_type: Optional[str] = None  # For weapons, e.g., "slashing"
    armor_class: Optional[int] = None  # For armor/shields
    properties: List[str] = []  # e.g., ["finesse", "light", "versatile"]

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
    equipped_slots: List[EquipmentSlot] = []  # Which slots this item is equipped in

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
    available_classes: List[str] = []  # Classes that can learn this spell

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
    spell_slots: List[SpellSlot] = []
    known_spells: List[str] = []  # Spell IDs
    prepared_spells: List[str] = []  # Subset of known spells that are prepared
    cantrips_known: List[str] = []  # Cantrip IDs
    concentration_spell: Optional[str] = None  # Currently concentrating spell ID
    
class ConcentrationSpell(BaseModel):
    spell_id: str
    character_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    duration_rounds: Optional[int] = None
    save_dc: int = 10  # Base concentration DC

class CharacterSheet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    race: Race
    character_class: CharacterClass
    level: int = 1
    background: Optional[str] = None
    alignment: Optional[str] = None
    experience: int = 0
    abilities: Abilities
    hit_points: HitPoints
    armor_class: int = 10
    speed: int = 30
    proficiency_bonus: int = 2
    skills: Dict[str, bool] = {}
    inventory: List[InventorySlot] = []
    equipped_items: List[EquippedItem] = []
    carrying_capacity: Optional[float] = None
    spells: List[Spell] = []
    spellcasting: Optional[SpellCasting] = None
    features: List[Dict[str, Any]] = []
    backstory: Optional[str] = None
    # Progression tracking
    ability_score_improvements_used: int = 0
    hit_dice: str = "1d8"  # Class-specific hit dice (e.g., "1d8" for rogues, "1d10" for fighters)

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
    actions: List[Dict[str, Any]]
    abilities: Optional[Abilities] = None
    armor_class: int = 10

class CombatEncounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: CombatState = CombatState.READY
    enemies: List[Enemy]
    round: int = 0
    current_turn: Optional[int] = None
    turn_order: List[CombatParticipant] = []
    narrative_context: Dict[str, Any] = {}

# NPC System Models
class NPCPersonality(BaseModel):
    traits: List[str] = []  # Personality traits
    ideals: List[str] = []  # Core beliefs
    bonds: List[str] = []   # Important connections
    flaws: List[str] = []   # Character flaws
    mannerisms: List[str] = []  # Speech patterns, habits
    appearance: Optional[str] = None
    motivations: List[str] = []

class NPCRelationship(BaseModel):
    character_id: str
    relationship_type: str  # "friend", "enemy", "neutral", "ally", "rival"
    trust_level: int = 0  # -100 to 100
    notes: Optional[str] = None

class NPCInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    npc_id: str
    character_id: Optional[str] = None  # None for party interactions
    interaction_type: str  # "conversation", "combat", "trade", "quest"
    timestamp: datetime = Field(default_factory=datetime.now)
    summary: str
    outcome: Optional[str] = None
    relationship_change: int = 0  # Change in trust/reputation

class NPC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    campaign_id: str
    
    # Personality and behavior
    personality: NPCPersonality = NPCPersonality()
    voice_description: Optional[str] = None
    
    # Game mechanics
    level: int = 1
    abilities: Optional[Abilities] = None
    hit_points: Optional[HitPoints] = None
    armor_class: Optional[int] = None
    skills: Dict[str, int] = {}  # Skill bonuses
    
    # Relationships and interactions
    relationships: List[NPCRelationship] = []
    interaction_history: List[str] = []  # List of interaction IDs
    
    # Story relevance
    importance: str = "minor"  # "minor", "major", "critical"
    story_role: Optional[str] = None  # "merchant", "quest_giver", "antagonist", etc.
    quest_involvement: List[str] = []  # Quest IDs
    
    # Status
    is_alive: bool = True
    current_mood: str = "neutral"  # "friendly", "hostile", "neutral", "suspicious"
    notes: Optional[str] = None

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    setting: str
    dm_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    characters: List[str] = []  # Character IDs
    locations: Dict[str, Any] = {}
    npcs: Dict[str, Any] = {}
    quests: Dict[str, Any] = {}
    current_location: Optional[str] = None
    tone: str = "heroic"
    homebrew_rules: List[str] = []
    session_log: List[Dict[str, Any]] = []
    state: str = "created"
    world_description: Optional[str] = None
    world_art: Optional[Dict[str, Any]] = None
    is_template: bool = False
    is_custom: bool = True
    template_id: Optional[str] = None  # For cloned campaigns
    plot_hooks: List[str] = []
    key_npcs: List[str] = []

# Request/Response models
class CreateCharacterRequest(BaseModel):
    name: str
    race: Race
    character_class: CharacterClass
    abilities: Abilities
    backstory: Optional[str] = None

class LevelUpRequest(BaseModel):
    character_id: str
    ability_improvements: Optional[Dict[str, int]] = None  # {"strength": 1, "dexterity": 1} for +2 ASI
    feat_choice: Optional[str] = None  # Name of feat if chosen instead of ASI

class LevelUpResponse(BaseModel):
    success: bool
    new_level: int
    hit_points_gained: int
    ability_improvements: Dict[str, int]
    new_proficiency_bonus: int
    features_gained: List[str]
    message: str

class PlayerInput(BaseModel):
    message: str
    character_id: str
    campaign_id: str

class GameResponse(BaseModel):
    message: str
    images: List[str] = []
    state_updates: Dict[str, Any] = {}
    combat_updates: Optional[Dict[str, Any]] = None

class CreateCampaignRequest(BaseModel):
    name: str
    setting: str 
    tone: Optional[str] = "heroic"
    homebrew_rules: Optional[List[str]] = []
    description: Optional[str] = None

class CampaignUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    setting: Optional[str] = None
    tone: Optional[str] = None
    homebrew_rules: Optional[List[str]] = None
    world_description: Optional[str] = None

class CloneCampaignRequest(BaseModel):
    template_id: str
    new_name: Optional[str] = None

class CampaignListResponse(BaseModel):
    campaigns: List[Campaign]
    templates: List[Campaign]

class AIAssistanceRequest(BaseModel):
    text: str
    context_type: str  # "setting", "description", "plot_hook", etc.
    campaign_tone: Optional[str] = "heroic"

class AIAssistanceResponse(BaseModel):
    suggestions: List[str]
    enhanced_text: Optional[str] = None

class GenerateImageRequest(BaseModel):
    image_type: str  # "character_portrait", "scene_illustration", "item_visualization"
    details: Dict[str, Any]

class BattleMapRequest(BaseModel):
    environment: Dict[str, Any]
    combat_context: Optional[Dict[str, Any]] = None

# Narrative Generation Models
class NarrativeChoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    description: Optional[str] = None
    consequences: Dict[str, Any] = {}
    requirements: Dict[str, Any] = {}  # Conditions that must be met to show this choice
    weight: float = 1.0  # Probability weight for random selection

class PlotPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: str  # "introduction", "conflict", "climax", "resolution", "subplot"
    status: str = "pending"  # "pending", "active", "completed", "skipped"
    dependencies: List[str] = []  # IDs of plot points that must be completed first
    triggers: Dict[str, Any] = {}  # Conditions that activate this plot point
    outcomes: Dict[str, Any] = {}  # Results when this plot point is completed
    importance: int = 5  # 1-10 scale
    estimated_duration: Optional[int] = None  # Expected number of scenes/sessions

class StoryArc(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: str  # "main", "side", "character", "world"
    status: str = "planning"  # "planning", "active", "paused", "completed"
    plot_points: List[str] = []  # PlotPoint IDs in order
    current_point: Optional[str] = None  # Current active plot point ID
    characters_involved: List[str] = []
    themes: List[str] = []
    estimated_length: Optional[int] = None  # Expected number of sessions
    player_choices: List[str] = []  # NarrativeChoice IDs that influenced this arc

class NarrativeState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    current_scene: Optional[str] = None
    active_story_arcs: List[str] = []  # StoryArc IDs
    completed_story_arcs: List[str] = []  # StoryArc IDs  
    pending_choices: List[str] = []  # NarrativeChoice IDs available to players
    narrative_flags: Dict[str, Any] = {}  # Story flags and variables
    character_relationships: Dict[str, Dict[str, Any]] = {}  # Character interaction history
    world_state: Dict[str, Any] = {}  # Current state of locations, factions, etc.
    last_updated: datetime = Field(default_factory=datetime.now)

class NarrativeEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: str  # "choice_made", "plot_point_completed", "character_interaction", "world_change"
    timestamp: datetime = Field(default_factory=datetime.now)
    characters_involved: List[str] = []
    location: Optional[str] = None
    choices_made: List[str] = []  # NarrativeChoice IDs
    consequences: Dict[str, Any] = {}
    story_arc_id: Optional[str] = None
    plot_point_id: Optional[str] = None

class SpellAttackBonusRequest(BaseModel):
    character_class: CharacterClass
    level: int
    spellcasting_ability_score: int

# Spell-related request and response models
class ManageSpellsRequest(BaseModel):
    character_id: str
    action: str  # "learn", "forget", "prepare", "unprepare"
    spell_ids: List[str]

class ManageSpellSlotsRequest(BaseModel):
    character_id: str
    action: str  # "use", "recover", "set"
    slot_level: int
    count: Optional[int] = 1

class CastSpellRequest(BaseModel):
    combat_id: str
    character_id: str
    spell_id: str
    slot_level: int
    target_ids: Optional[List[str]] = []
    spell_attack_roll: Optional[int] = None

class SpellListRequest(BaseModel):
    character_class: Optional[CharacterClass] = None
    spell_level: Optional[int] = None
    school: Optional[str] = None

class ConcentrationRequest(BaseModel):
    character_id: str
    action: str  # "start", "end", "check"
    spell_id: Optional[str] = None
    damage_taken: Optional[int] = None

class SpellListResponse(BaseModel):
    spells: List[Spell]
    total_count: int

class SpellCastingResponse(BaseModel):
    success: bool
    message: str
    spell_effects: Dict[str, Any] = {}
    concentration_broken: bool = False
    slot_used: bool = False

class ConcentrationCheckResponse(BaseModel):
    success: bool
    concentration_maintained: bool
    dc: int
    roll_result: Optional[int] = None
    spell_ended: bool = False

# Inventory-related request and response models
class ManageEquipmentRequest(BaseModel):
    character_id: str
    action: str  # "equip", "unequip"
    equipment_id: str
    slot: Optional[EquipmentSlot] = None

class EncumbranceRequest(BaseModel):
    character_id: str

class MagicalEffectsRequest(BaseModel):
    character_id: str
    item_id: str
    action: str  # "apply", "remove"

class ItemCatalogRequest(BaseModel):
    item_type: Optional[ItemType] = None
    rarity: Optional[ItemRarity] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

class EquipmentResponse(BaseModel):
    success: bool
    message: str
    stat_changes: Dict[str, int] = {}
    armor_class_change: Optional[int] = None

class EncumbranceResponse(BaseModel):
    character_id: str
    current_weight: float
    carrying_capacity: float
    encumbrance_level: str  # "unencumbered", "encumbered", "heavily_encumbered"
    speed_penalty: int = 0

class ItemCatalogResponse(BaseModel):
    items: List[Equipment]
    total_count: int

class MagicalEffectsResponse(BaseModel):
    success: bool
    message: str
    active_effects: List[str]
    stat_modifiers: Dict[str, int]

# NPC-related request and response models
class CreateNPCRequest(BaseModel):
    campaign_id: str
    name: str
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    importance: str = "minor"
    story_role: Optional[str] = None

class UpdateNPCRequest(BaseModel):
    name: Optional[str] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    current_mood: Optional[str] = None
    notes: Optional[str] = None

class NPCInteractionRequest(BaseModel):
    npc_id: str
    character_id: Optional[str] = None
    interaction_type: str
    summary: str
    outcome: Optional[str] = None
    relationship_change: int = 0

class GenerateNPCStatsRequest(BaseModel):
    npc_id: str
    level: Optional[int] = None
    role: str = "civilian"  # "civilian", "guard", "soldier", "spellcaster", "rogue"

class NPCPersonalityRequest(BaseModel):
    npc_id: str

class NPCListResponse(BaseModel):
    npcs: List[NPC]
    total_count: int

class NPCInteractionResponse(BaseModel):
    success: bool
    message: str
    interaction_id: str
    new_relationship_level: Optional[int] = None

class NPCStatsResponse(BaseModel):
    success: bool
    message: str
    generated_stats: Dict[str, Any]
