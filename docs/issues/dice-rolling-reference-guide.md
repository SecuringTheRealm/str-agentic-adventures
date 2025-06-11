# Dice Rolling System - Current vs Proposed Capabilities

## Quick Reference Guide

### Currently Supported ✅

| Expression | Description | Example Result |
|------------|-------------|----------------|
| `1d20` | Single d20 roll | `{"rolls": [15], "total": 15}` |
| `2d6+3` | 2d6 with +3 modifier | `{"rolls": [4,6], "modifier": 3, "total": 13}` |
| `3d8-2` | 3d8 with -2 modifier | `{"rolls": [2,7,1], "modifier": -2, "total": 8}` |
| `d20` | Implicit 1d20 | `{"rolls": [12], "total": 12}` |

### Advanced Features Proposed 🚀

| Expression | Description | Use Case | Example |
|------------|-------------|----------|---------|
| `4d6dl1` | Drop lowest 1 | Ability score generation | `[6,4,2,5] → [6,4,5] = 15` |
| `4d6dh1` | Drop highest 1 | Disadvantage scenarios | `[6,4,2,5] → [4,2,5] = 11` |
| `2d20kh1` | Keep highest 1 | Advantage attacks | `[8,15] → 15` |
| `2d20kl1` | Keep lowest 1 | Disadvantage attacks | `[8,15] → 8` |
| `1d6r1` | Reroll on 1 | Great Weapon Fighting | `[1] → reroll → [4]` |
| `1d6r≤2` | Reroll 1-2 | Halfling Lucky | `[2] → reroll → [5]` |
| `1d6!` | Exploding dice | Critical chains | `[6] → [6,4] = 10` |
| `3d6+2d4+5` | Multiple pools | Complex spells | `[4,2,6] + [3,1] + 5 = 21` |

### D&D 5e Specific Scenarios

#### Character Creation
```python
# Generate all ability scores
ability_scores = generate_ability_scores()
# Equivalent to: STR=4d6dl1, DEX=4d6dl1, CON=4d6dl1, etc.
```

#### Combat Rolls
```python
# Attack with advantage (hidden rogue)
attack_roll = roll_with_context("1d20", advantage=True, character=rogue)
# Auto-applies: 1d20 (advantage) + DEX modifier + proficiency + weapon bonus

# Damage with sneak attack  
damage_roll = roll_with_context("1d6+3d6", character=rogue)
# Weapon damage + sneak attack damage + DEX modifier
```

#### Spell Casting
```python
# Fireball (8d6) with save for half
fireball = roll_spell_damage("8d6", spell_level=3, save_dc=15, targets=targets)
# Handles saves, resistance, immunity automatically
```

### Integration Features

#### Manual Roll Input
```python
# Player uses physical dice
manual_result = input_manual_roll("d20", result=18, context="stealth_check")
# System applies: 18 + DEX(+4) + proficiency(+3) + expertise(+3) = 28
```

#### Roll History & Analytics
```python
# Session tracking
session_rolls = get_session_rolls()
# Returns: all rolls with timestamps, context, and results

# Statistical analysis
roll_stats = analyze_roll_statistics(session_rolls)
# Average, distribution, potential bias detection
```

### Advantage/Disadvantage Consolidation

#### Current Implementation Issues
- Advantage logic duplicated in `skill_check()` and `resolve_attack()`
- No centralized advantage/disadvantage handling
- Missing support for multiple sources of advantage

#### Proposed Solution
```python
def apply_advantage_disadvantage(base_expression: str, 
                                advantage_sources: List[str] = None,
                                disadvantage_sources: List[str] = None) -> RollResult:
    """
    Centralized advantage/disadvantage logic
    
    Examples:
    - advantage_sources: ["hidden", "guiding_bolt"]  
    - disadvantage_sources: ["prone", "darkness"]
    - Net result: advantage, disadvantage, or normal based on sources
    """
```

### Error Handling & Validation

#### Current Limitations
- Basic error messages: "Invalid dice notation"
- No context about what went wrong
- No suggestions for correction

#### Enhanced Error Handling
```python
# Invalid expression
roll_dice("2d6+")  
# Returns: {
#   "error": "Missing modifier value after '+'", 
#   "suggestion": "Try '2d6+3' or '2d6-2'",
#   "position": 4
# }

# Character context validation  
roll_with_context("1d20+10", character=level1_fighter)
# Returns: {
#   "warning": "Modifier +10 unusually high for level 1 character",
#   "breakdown": "1d20 + ??? (+10) - please verify modifier source"
# }
```

### Performance Considerations

#### Current Performance
- Simple expressions: ~1ms
- Complex expressions: N/A (not supported)

#### Target Performance  
- Simple expressions: ~1ms (no regression)
- Complex expressions: <50ms parsing, <100ms execution
- Roll history: <10MB memory for typical session
- Character context lookup: <5ms

### Migration Strategy

#### Backward Compatibility
```python
# Existing code continues to work unchanged
result = plugin.roll_dice("2d6+3")  # ✅ Still works

# New features available through enhanced methods
result = plugin.roll_advanced("4d6dl1")  # ✅ New functionality
result = plugin.roll_with_context("1d20", character=pc)  # ✅ Enhanced
```

#### Gradual Enhancement
1. **Phase 1**: Add advanced notation support (backward compatible)
2. **Phase 2**: Add character context integration (opt-in)  
3. **Phase 3**: Add manual input and history (additive features)
4. **Phase 4**: Performance optimization and analytics

---

## Summary

This enhancement transforms the dice rolling system from basic notation support to a comprehensive D&D 5e gaming engine while maintaining full backward compatibility. The new system supports all standard D&D mechanics, integrates seamlessly with character sheets, and provides the flexibility needed for both digital and hybrid (physical + digital) gameplay.