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

class ActionType(str, Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    MOVEMENT = "movement"
    REACTION = "reaction"
    FREE = "free"

class Condition(str, Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"

class DamageType(str, Enum):
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"

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

class ActiveCondition(BaseModel):
    condition: Condition
    duration: int = -1  # -1 for permanent until removed
    source: str  # What caused the condition
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None

class CombatAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    action_type: ActionType
    damage_dice: Optional[str] = None
    damage_type: Optional[DamageType] = None
    attack_bonus: Optional[int] = None
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None
    range: str = "5 feet"
    area_of_effect: Optional[Dict[str, Any]] = None
    conditions_applied: List[str] = []
    spell_level: Optional[int] = None
    description: Optional[str] = None

class TurnResources(BaseModel):
    actions_remaining: int = 1
    bonus_actions_remaining: int = 1
    movement_remaining: int = 30
    reactions_remaining: int = 1

class SpellSlot(BaseModel):
    level: int
    total: int
    used: int

class SpellcastingStats(BaseModel):
    spell_attack_bonus: int
    spell_save_dc: int
    spellcasting_ability: Ability
    spell_slots: Dict[int, SpellSlot] = {}  # level -> slots
    concentration_spell: Optional[str] = None

class CombatSpell(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    level: int
    casting_time: ActionType
    range: str
    area_of_effect: Optional[Dict[str, Any]] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[DamageType] = None
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None
    concentration: bool = False
    conditions_applied: List[str] = []
    description: Optional[str] = None

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
    # Enhanced combat features
    spellcasting_stats: Optional[SpellcastingStats] = None
    active_conditions: List[ActiveCondition] = []
    available_actions: List[CombatAction] = []
    damage_resistances: List[DamageType] = []
    damage_immunities: List[DamageType] = []
    damage_vulnerabilities: List[DamageType] = []

class CombatParticipant(BaseModel):
    id: str
    name: str
    initiative: int
    type: str  # "player" or "enemy"
    turn_resources: TurnResources = Field(default_factory=TurnResources)
    active_conditions: List[ActiveCondition] = []
    position: Optional[Dict[str, int]] = None  # x, y coordinates on battle map

class Enemy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    level: int
    hit_points: HitPoints
    initiative: int = 0
    actions: List[Dict[str, Any]]
    abilities: Optional[Abilities] = None
    armor_class: int = 10
    # Enhanced combat features
    available_actions: List[CombatAction] = []
    active_conditions: List[ActiveCondition] = []
    damage_resistances: List[DamageType] = []
    damage_immunities: List[DamageType] = []
    damage_vulnerabilities: List[DamageType] = []

class CombatEncounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: CombatState = CombatState.READY
    enemies: List[Enemy]
    round: int = 0
    current_turn: Optional[int] = None
    turn_order: List[CombatParticipant] = []
    narrative_context: Dict[str, Any] = {}
    # Enhanced tracking
    environmental_effects: List[Dict[str, Any]] = []
    victory_conditions: Dict[str, Any] = {}
    participants: Dict[str, Dict[str, Any]] = {}  # id -> participant data

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
