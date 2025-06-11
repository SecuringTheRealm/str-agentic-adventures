# Enhanced D&D 5e Combat System Implementation

## Issue Summary

Implement a comprehensive D&D 5e combat system that provides turn-based combat, proper initiative tracking, and full integration with character stats and abilities. The current combat implementation in `CombatMCAgent` provides basic functionality but lacks many core D&D 5e mechanics needed for an authentic tabletop experience.

## Problem Statement

The current combat system is missing several critical D&D 5e features:

1. **Action Economy**: No support for Actions, Bonus Actions, Movement, and Reactions
2. **Combat Actions**: Limited action types beyond basic attacks
3. **Conditions & Status Effects**: No implementation of D&D 5e conditions (prone, stunned, etc.)
4. **Spell Integration**: No spell casting mechanics in combat
5. **Advanced Combat Features**: Missing opportunity attacks, cover, advantage/disadvantage contexts
6. **Damage Types & Resistances**: No support for different damage types and creature resistances
7. **Area of Effect**: No support for AoE spells and abilities
8. **Concentration**: No concentration mechanics for spells

## Current State Analysis

### Existing Implementation (✅ Completed)
- Basic initiative rolling and turn order sorting
- Simple enemy creation and scaling
- Basic attack resolution through `RulesEnginePlugin`
- Combat state tracking (ready, active, completed)
- Integration with `CombatCartographer` for battle maps

### Current Files
- `backend/app/agents/combat_mc_agent.py` - Main combat logic
- `backend/app/plugins/rules_engine_plugin.py` - D&D 5e mechanics
- `backend/app/models/game_models.py` - Data models
- `backend/app/agents/combat_cartographer_agent.py` - Battle map generation

## Technical Requirements

### 1. Enhanced Action Economy System

**New Models Needed:**
```python
class ActionType(str, Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    MOVEMENT = "movement"
    REACTION = "reaction"
    FREE = "free"

class CombatAction(BaseModel):
    id: str
    name: str
    action_type: ActionType
    damage_dice: Optional[str] = None
    attack_bonus: Optional[int] = None
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None
    range: str = "5 feet"
    area_of_effect: Optional[Dict[str, Any]] = None
    conditions_applied: List[str] = []
    spell_level: Optional[int] = None

class TurnResources(BaseModel):
    actions_remaining: int = 1
    bonus_actions_remaining: int = 1
    movement_remaining: int = 30
    reactions_remaining: int = 1
```

**Implementation Tasks:**
- [ ] Create action economy models and enums
- [ ] Implement turn resource tracking per participant
- [ ] Add action validation (can't take two Actions per turn)
- [ ] Build action selection interface for players

### 2. Combat Conditions System

**New Models Needed:**
```python
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

class ActiveCondition(BaseModel):
    condition: Condition
    duration: int = -1  # -1 for permanent until removed
    source: str  # What caused the condition
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None
```

**Implementation Tasks:**
- [ ] Create condition system with duration tracking
- [ ] Implement condition effects on stats and abilities
- [ ] Add automatic condition removal (end of turn, save successful)
- [ ] Integrate conditions with attack rolls and ability checks

### 3. Spell System Integration

**Enhancements to Existing Models:**
```python
class SpellSlot(BaseModel):
    level: int
    total: int
    used: int

class SpellcastingStats(BaseModel):
    spell_attack_bonus: int
    spell_save_dc: int
    spellcasting_ability: Ability
    spell_slots: Dict[int, SpellSlot]  # level -> slots
    concentration_spell: Optional[str] = None

class CombatSpell(BaseModel):
    id: str
    name: str
    level: int
    casting_time: ActionType
    range: str
    area_of_effect: Optional[Dict[str, Any]] = None
    damage_dice: Optional[str] = None
    save_dc: Optional[int] = None
    save_ability: Optional[Ability] = None
    concentration: bool = False
    conditions_applied: List[str] = []
```

**Implementation Tasks:**
- [ ] Add spellcasting stats to character models
- [ ] Implement spell slot tracking and consumption
- [ ] Add concentration mechanics and saving throws
- [ ] Create spell targeting and area-of-effect resolution

### 4. Advanced Combat Mechanics

**New Plugin Functions Needed:**
```python
# In RulesEnginePlugin
def calculate_opportunity_attack(self, trigger_action: str, position_data: Dict) -> Dict[str, Any]
def resolve_saving_throw(self, save_dc: int, ability: Ability, character_stats: Dict) -> Dict[str, Any]
def apply_damage_resistance(self, damage: int, damage_type: str, resistances: List[str]) -> int
def check_concentration(self, damage_taken: int, concentration_bonus: int) -> Dict[str, Any]
```

**Implementation Tasks:**
- [ ] Add opportunity attack mechanics
- [ ] Implement saving throws with automatic rolling
- [ ] Add damage type system and resistance calculation
- [ ] Create cover mechanics and AC adjustments
- [ ] Implement concentration checks when taking damage

### 5. Enhanced CombatMCAgent Methods

**New Methods Needed:**
```python
async def process_action(self, encounter_id: str, participant_id: str, action: CombatAction) -> Dict[str, Any]
async def apply_condition(self, encounter_id: str, target_id: str, condition: ActiveCondition) -> Dict[str, Any]
async def remove_condition(self, encounter_id: str, target_id: str, condition: Condition) -> Dict[str, Any]
async def process_spell_cast(self, encounter_id: str, caster_id: str, spell: CombatSpell, targets: List[str]) -> Dict[str, Any]
async def end_turn(self, encounter_id: str, participant_id: str) -> Dict[str, Any]
async def check_victory_conditions(self, encounter_id: str) -> Dict[str, Any]
```

**Implementation Tasks:**
- [ ] Refactor `process_combat_action` to handle different action types
- [ ] Add turn management with proper resource reset
- [ ] Implement automatic end-of-turn processing (condition duration, regeneration)
- [ ] Add victory/defeat condition checking

### 6. Integration Enhancements

**Combat Cartographer Integration:**
- [ ] Add position tracking for tactical combat
- [ ] Implement movement validation and range calculation
- [ ] Add support for area-of-effect targeting visualization

**Narrator Integration:**
- [ ] Enhanced combat narrative generation
- [ ] Condition and spell effect descriptions
- [ ] Dynamic combat environment reactions

## Acceptance Criteria

### Core Functionality
- [ ] Players can take Actions, Bonus Actions, move, and use Reactions per D&D 5e rules
- [ ] All D&D 5e conditions are implemented with proper mechanical effects
- [ ] Spell casting works with slot consumption and concentration mechanics
- [ ] Initiative system properly handles ties and delays
- [ ] Combat automatically ends when victory/defeat conditions are met

### Rule Compliance
- [ ] Attack rolls follow D&D 5e advantage/disadvantage rules
- [ ] Saving throws are properly calculated with proficiency bonuses
- [ ] Damage resistance and immunity work correctly
- [ ] Opportunity attacks trigger automatically when appropriate
- [ ] Concentration checks occur when spellcasters take damage

### Integration
- [ ] Character sheet data properly feeds into combat calculations
- [ ] Battle map positions affect range and area-of-effect spells
- [ ] Combat outcomes update character resources (HP, spell slots, etc.)
- [ ] Narrative descriptions enhance the tactical combat experience

## Testing Requirements

- [ ] Unit tests for all new rule mechanics
- [ ] Integration tests for combat flow with multiple participants
- [ ] Edge case testing for complex spell interactions
- [ ] Performance testing for large encounters (8+ participants)

## Implementation Priority

1. **High Priority**: Action economy and turn management
2. **High Priority**: Condition system implementation
3. **Medium Priority**: Spell system integration
4. **Medium Priority**: Advanced combat mechanics (opportunity attacks, cover)
5. **Low Priority**: Complex spell interactions and edge cases

## Dependencies

- Existing `RulesEnginePlugin` functionality
- Character sheet data from `Scribe` agent
- Battle map positioning from `CombatCartographer`
- Narrative integration with `Narrator` agent

## Estimated Effort

- **Development**: 3-4 weeks for a 2-person team
- **Testing**: 1 week
- **Integration**: 1 week
- **Documentation**: 3-5 days

## Related Issues

- Character sheet enhancement for spell tracking
- Battle map positioning system
- Narrative combat description improvements

---

This enhancement will transform the basic combat system into a fully-featured D&D 5e combat engine that provides an authentic tabletop experience within the AI Dungeon Master platform.