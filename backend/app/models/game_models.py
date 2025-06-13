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
    value: Optional[int] = None
    rarity: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

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
    inventory: List[Item] = []
    spells: List[Spell] = []
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
