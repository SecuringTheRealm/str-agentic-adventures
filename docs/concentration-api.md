# Concentration Management API

This API allows for tracking and managing spell concentration for characters, implementing D&D 5e concentration mechanics.

## Overview

Concentration is a crucial mechanic in D&D 5e that requires a character to maintain focus on certain spells. This implementation provides:

- Starting concentration on a spell
- Ending concentration voluntarily
- Automatic concentration checks when taking damage
- Proper D&D 5e concentration save calculations

## API Endpoint

### POST `/character/{character_id}/concentration`

Manages spell concentration for a specific character.

#### Request Body

```json
{
  "action": "start|end|check",
  "spell_name": "Fireball",      // Required for "start" action
  "spell_level": 3,              // Optional for "start" action
  "damage_taken": 24             // Required for "check" action
}
```

#### Response

```json
{
  "success": true,
  "action_performed": "start|end|check",
  "concentration_status": {
    "spell_name": "Fireball",
    "spell_level": 3,
    "duration_remaining": null,
    "save_dc": null
  },
  "check_result": {              // Only present for "check" action
    "dice_roll": 15,
    "constitution_modifier": 2,
    "proficiency_bonus": 2,
    "total_save": 19,
    "save_dc": 12,
    "success": true,
    "damage_taken": 24
  },
  "message": "Started concentrating on Fireball"
}
```

## Actions

### Start Concentration (`"action": "start"`)

- **Purpose**: Begin concentrating on a new spell
- **Required Parameters**: `spell_name`
- **Optional Parameters**: `spell_level`
- **Behavior**: 
  - If already concentrating on another spell, automatically ends the previous concentration
  - Sets the new concentration status
- **Example**:
  ```json
  {
    "action": "start",
    "spell_name": "Hold Person",
    "spell_level": 2
  }
  ```

### End Concentration (`"action": "end"`)

- **Purpose**: Voluntarily stop concentrating on current spell
- **Required Parameters**: None
- **Behavior**: 
  - Clears concentration status
  - Returns error if not currently concentrating
- **Example**:
  ```json
  {
    "action": "end"
  }
  ```

### Check Concentration (`"action": "check"`)

- **Purpose**: Make a concentration saving throw (typically due to taking damage)
- **Required Parameters**: `damage_taken`
- **Behavior**: 
  - Calculates save DC: `max(10, damage_taken / 2)`
  - Rolls 1d20 + Constitution modifier + proficiency bonus
  - If save fails, ends concentration
  - If save succeeds, maintains concentration
- **Example**:
  ```json
  {
    "action": "check",
    "damage_taken": 30
  }
  ```

## D&D 5e Rules Implementation

### Concentration Save DC
- **Base DC**: 10
- **Damage DC**: Half the damage taken (rounded down)
- **Final DC**: The higher of base DC (10) or damage DC

### Concentration Save Bonus
- **Base Roll**: 1d20
- **Constitution Modifier**: `(Constitution Score - 10) / 2` (rounded down)
- **Proficiency Bonus**: Based on character level
- **Total**: Roll + Constitution modifier + proficiency bonus

### Automatic Spell Switching
When starting concentration on a new spell while already concentrating on another:
1. Previous concentration is automatically ended
2. New concentration begins immediately
3. No concentration check required for the switch

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **404**: Character not found
- **400**: Invalid action or missing required parameters
- **500**: Internal server error

Example error response:
```json
{
  "detail": "Character char_123 not found"
}
```

## Usage Examples

### Starting Concentration
```bash
curl -X POST "http://localhost:8000/api/game/character/char_123/concentration" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "spell_name": "Counterspell",
    "spell_level": 3
  }'
```

### Concentration Check After Taking Damage
```bash
curl -X POST "http://localhost:8000/api/game/character/char_123/concentration" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "check",
    "damage_taken": 18
  }'
```

### Ending Concentration
```bash
curl -X POST "http://localhost:8000/api/game/character/char_123/concentration" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "end"
  }'
```

## Character Data Model Updates

The character data model now includes a `concentration` field:

```json
{
  "concentration": {
    "spell_name": "Web",
    "spell_level": 2,
    "duration_remaining": null,
    "save_dc": null
  }
}
```

- `spell_name`: Name of the spell being concentrated on
- `spell_level`: Level at which the spell was cast
- `duration_remaining`: Optional field for tracking spell duration (in rounds/minutes)
- `save_dc`: Optional field for storing spell save DC if needed

When not concentrating, this field is `null`.