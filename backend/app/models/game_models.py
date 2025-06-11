"""
Data models for the AI Dungeon Master application.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
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

# Request/Response models
class CreateCharacterRequest(BaseModel):
    name: str
    race: Race
    character_class: CharacterClass
    abilities: Abilities
    backstory: Optional[str] = None

class PlayerInput(BaseModel):
    message: str
    character_id: str
    campaign_id: str

class GameResponse(BaseModel):
    message: str
    images: List[str] = []
    state_updates: Dict[str, Any] = {}
    combat_updates: Optional[Dict[str, Any]] = None
    
class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    setting: str
    tone: str = "heroic"
    homebrew_rules: List[str] = []
    characters: List[str] = []
    session_log: List[Dict[str, Any]] = []
    state: str = "created"
    world_description: Optional[str] = None
    world_art: Optional[Dict[str, Any]] = None

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

# Session management models
class GameSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    campaign_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_saved: datetime = Field(default_factory=datetime.now)
    characters: Dict[str, Any] = {}
    narrative_memory: Dict[str, Any] = {}
    campaign_state: Dict[str, Any] = {}
    session_log: List[Dict[str, Any]] = []

class CreateSessionRequest(BaseModel):
    campaign_id: str
    name: Optional[str] = None

class SaveSessionRequest(BaseModel):
    session_id: str
    session_data: Dict[str, Any]

class SessionMetadata(BaseModel):
    id: str
    name: str
    campaign_id: str
    created_at: str
    last_saved: str
