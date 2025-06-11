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

# NPC Management Models
class NPCPersonality(str, Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    SUSPICIOUS = "suspicious"
    HELPFUL = "helpful"
    GREEDY = "greedy"
    PROUD = "proud"
    HUMBLE = "humble"
    CURIOUS = "curious"
    FEARFUL = "fearful"

class NPCRole(str, Enum):
    MERCHANT = "merchant"
    GUARD = "guard"
    INNKEEPER = "innkeeper"
    NOBLE = "noble"
    COMMONER = "commoner"
    CRIMINAL = "criminal"
    SCHOLAR = "scholar"
    PRIEST = "priest"
    ARTISAN = "artisan"
    SOLDIER = "soldier"
    QUEST_GIVER = "quest_giver"
    ALLY = "ally"
    RIVAL = "rival"

class NPCBehavior(BaseModel):
    """Defines how an NPC behaves in different situations"""
    default_attitude: NPCPersonality = NPCPersonality.NEUTRAL
    combat_behavior: str = "defensive"  # aggressive, defensive, flee, support
    conversation_style: str = "polite"  # polite, gruff, eloquent, simple, cryptic
    trust_level: int = Field(default=5, ge=0, le=10)  # 0=completely distrustful, 10=completely trusting
    bravery: int = Field(default=5, ge=0, le=10)  # 0=cowardly, 10=heroic
    intelligence: int = Field(default=5, ge=0, le=10)  # affects dialogue complexity
    helpfulness: int = Field(default=5, ge=0, le=10)  # willingness to help players
    
class NPCRelationship(BaseModel):
    """Tracks relationship between NPC and a character/other NPC"""
    target_id: str  # Character or NPC ID
    target_type: str  # "character" or "npc"
    relationship_type: str  # "friend", "enemy", "neutral", "family", "employer", etc.
    affection: int = Field(default=0, ge=-10, le=10)  # -10=hatred, 0=neutral, 10=love
    trust: int = Field(default=0, ge=-10, le=10)  # -10=complete distrust, 10=complete trust
    respect: int = Field(default=0, ge=-10, le=10)  # -10=contempt, 10=admiration
    history: List[str] = []  # List of significant interactions
    last_interaction: Optional[datetime] = None

class NPCMemory(BaseModel):
    """What the NPC remembers about interactions and events"""
    important_facts: List[str] = []  # Key facts the NPC knows
    player_interactions: List[Dict[str, Any]] = []  # History of player interactions
    witnessed_events: List[str] = []  # Events the NPC has witnessed
    rumors_heard: List[str] = []  # Rumors or information the NPC has heard
    secrets_known: List[str] = []  # Secrets the NPC knows (may or may not share)

class NPCInventory(BaseModel):
    """Items the NPC has"""
    items: List[Item] = []
    gold: int = 0
    will_trade: bool = False
    trade_markup: float = 1.2  # Price multiplier for selling to players
    preferred_items: List[str] = []  # Types of items they're interested in buying

class NPC(BaseModel):
    """Complete NPC model with behavior, relationships, and memory"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    race: Race
    role: NPCRole
    level: int = 1
    
    # Physical and basic attributes
    abilities: Optional[Abilities] = None
    hit_points: Optional[HitPoints] = None
    armor_class: int = 10
    age: Optional[int] = None
    appearance: Optional[str] = None
    
    # Location and status
    current_location: str
    home_location: Optional[str] = None
    is_alive: bool = True
    is_available: bool = True  # Can interact with players
    
    # Personality and behavior
    personality: NPCPersonality = NPCPersonality.NEUTRAL
    behavior: NPCBehavior = Field(default_factory=NPCBehavior)
    
    # Social connections
    relationships: List[NPCRelationship] = []
    faction: Optional[str] = None
    
    # Knowledge and memory
    memory: NPCMemory = Field(default_factory=NPCMemory)
    languages: List[str] = ["Common"]
    
    # Inventory and economics
    inventory: NPCInventory = Field(default_factory=NPCInventory)
    
    # Quest and story integration
    available_quests: List[str] = []  # Quest IDs this NPC can give
    involved_quests: List[str] = []  # Quest IDs this NPC is involved in
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None

class NPCInteraction(BaseModel):
    """Records an interaction between a player and an NPC"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    npc_id: str
    character_id: str
    interaction_type: str  # "conversation", "trade", "combat", "quest"
    context: Dict[str, Any] = {}  # Interaction details
    outcome: str  # "positive", "negative", "neutral"
    relationship_changes: Dict[str, int] = {}  # Changes to affection, trust, respect
    timestamp: datetime = Field(default_factory=datetime.now)

# Request/Response models for NPC management
class CreateNPCRequest(BaseModel):
    name: str
    description: str
    race: Race
    role: NPCRole
    current_location: str
    personality: Optional[NPCPersonality] = NPCPersonality.NEUTRAL
    level: Optional[int] = 1
    abilities: Optional[Abilities] = None
    behavior: Optional[NPCBehavior] = None

class UpdateNPCRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    current_location: Optional[str] = None
    is_available: Optional[bool] = None
    behavior: Optional[NPCBehavior] = None
    
class NPCInteractionRequest(BaseModel):
    character_id: str
    interaction_type: str
    message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

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
