# Finish Pending Issues (#533, #474, #514) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete three open issues — merge the already-done NPC models PR (#533), fix the last `next(get_session())` anti-pattern (#474), and implement short/long rest mechanics (#514).

**Architecture:** Three independent workstreams. #533 must merge first (it adds `DbDep` type alias used by #474). Then #474 and #514 execute in parallel worktrees. Each produces a PR that gets merged to main.

**Tech Stack:** Python/FastAPI backend, SQLAlchemy ORM, Pydantic models, React/TypeScript frontend, pytest

---

## Workstream A: Merge #533 (NPC Models) — Already Complete

### Task A1: Review and merge PR #533

**Files:** None (PR already has 682 additions across 8 files, all checkboxes checked)

- [ ] **Step 1: Check PR CI status**

```bash
gh pr checks 533
```

Expected: All checks pass (or only pre-existing failures)

- [ ] **Step 2: Merge the PR**

```bash
gh pr merge 533 --squash --delete-branch
```

- [ ] **Step 3: Update local main**

```bash
git checkout main && git pull --rebase origin main
```

- [ ] **Step 4: Close issue #530 (parent issue if not auto-closed)**

```bash
gh issue close 530 -c "Fixed in PR #533" 2>/dev/null || true
```

---

## Workstream B: Fix `next(get_session())` Anti-Pattern (#474)

**Depends on:** Workstream A (needs `DbDep` from #533 on main)

### Task B1: Fix combat.py anti-pattern

**Files:**
- Modify: `backend/app/routers/combat.py:183-209`
- Test: `backend/tests/test_concentration_integration.py` (verify existing tests still pass)

- [ ] **Step 1: Run existing tests to establish baseline**

```bash
cd backend && uv run pytest tests/ -v --tb=short -q 2>&1 | tail -20
```

Expected: Tests pass (note any pre-existing failures)

- [ ] **Step 2: Fix the anti-pattern in combat.py**

Replace the `_get_spell_data` function in `backend/app/routers/combat.py` (lines 183-209):

```python
async def _get_spell_data(spell_id: str) -> dict[str, Any]:
    """Get spell data from database or return default spell structure."""
    from app.database import get_session_context
    from app.models.db_models import Spell

    try:
        with get_session_context() as db:
            spell = db.query(Spell).filter(Spell.id == spell_id).first()
            if spell:
                return {
                    "id": spell.id,
                    "name": spell.name,
                    "level": spell.level,
                    "school": spell.school,
                    "damage_dice": spell.damage_dice,
                    "save_type": spell.save_type,
                    "concentration": spell.concentration,
                    "ritual": spell.ritual,
                    "components": spell.components,
                    "description": spell.description,
                    "higher_levels": spell.higher_levels,
                    **spell.data,
                }
    except Exception:
        pass

    return _get_default_spell_data(spell_id)
```

This replaces `next(get_session())` with the proper `get_session_context()` context manager (already exists in `database.py`).

- [ ] **Step 3: Run tests to verify fix**

```bash
cd backend && uv run pytest tests/test_concentration_integration.py tests/test_combat_edge_cases.py -v --tb=short
```

Expected: All pass

- [ ] **Step 4: Commit and push to existing PR branch**

```bash
git checkout copilot/fix-next-get-session-anti-pattern
git rebase main
git add backend/app/routers/combat.py
git commit -m "fix: replace next(get_session()) with get_session_context() in combat.py (closes #474)"
git push origin copilot/fix-next-get-session-anti-pattern --force-with-lease
```

- [ ] **Step 5: Update PR title and mark ready**

```bash
gh pr edit 474 --title "fix: replace next(get_session()) anti-pattern in combat.py"
gh pr ready 474
```

- [ ] **Step 6: Merge PR**

```bash
gh pr merge 474 --squash --delete-branch
```

- [ ] **Step 7: Close issue**

```bash
gh issue close 474 -c "Fixed in PR #474"
```

---

## Workstream C: Implement Short/Long Rest Mechanics (#514)

**Depends on:** Workstream A (needs main up to date)

### Task C1: Add hit dice tracking to CharacterSheet model

**Files:**
- Modify: `backend/app/models/game_models.py:195-222` (CharacterSheet class)

- [ ] **Step 1: Add hit dice tracking fields to CharacterSheet**

In `backend/app/models/game_models.py`, add to `CharacterSheet` after the `hit_dice` field (line 222):

```python
    hit_dice_remaining: int | None = None  # Defaults to level if None
    exhaustion_level: int = 0  # 0-6, 6 = death
```

### Task C2: Add rest request/response models

**Files:**
- Modify: `backend/app/models/game_models.py` (append after CharacterSheet-related models)

- [ ] **Step 1: Add rest models**

Append to `backend/app/models/game_models.py`:

```python
class RestType(str, Enum):
    SHORT = "short"
    LONG = "long"


class RestRequest(BaseModel):
    character_id: str
    rest_type: RestType
    hit_dice_to_spend: int = 0  # Only used for short rests


class RestResponse(BaseModel):
    success: bool
    message: str
    hp_recovered: int = 0
    spell_slots_recovered: list[int] = Field(default_factory=list)
    hit_dice_remaining: int = 0
    exhaustion_level: int = 0
```

### Task C3: Write failing tests for rest mechanics

**Files:**
- Create: `backend/tests/test_rest_mechanics.py`

- [ ] **Step 1: Write test file**

```python
"""Tests for short and long rest mechanics."""

import pytest
from app.models.game_models import (
    Abilities,
    CharacterClass,
    CharacterSheet,
    HitPoints,
    Race,
    RestRequest,
    RestType,
    SpellCasting,
    SpellSlot,
)


def _make_character(**overrides) -> CharacterSheet:
    """Create a test character with sensible defaults."""
    defaults = {
        "name": "Test Fighter",
        "race": Race.HUMAN,
        "character_class": CharacterClass.FIGHTER,
        "level": 5,
        "abilities": Abilities(strength=16, dexterity=14, constitution=14, intelligence=10, wisdom=12, charisma=8),
        "hit_points": HitPoints(current=20, maximum=44),
        "hit_dice": "1d10",
        "hit_dice_remaining": 5,
        "exhaustion_level": 0,
    }
    defaults.update(overrides)
    return CharacterSheet(**defaults)


class TestShortRest:
    """Test short rest mechanics."""

    def test_short_rest_spend_hit_dice_recovers_hp(self):
        from app.api.routes.rest_routes import calculate_short_rest
        char = _make_character(hit_points=HitPoints(current=20, maximum=44), hit_dice_remaining=5)
        result = calculate_short_rest(char, hit_dice_to_spend=2)
        assert result["hp_recovered"] > 0
        assert result["hit_dice_remaining"] == 3
        assert result["character"].hit_points.current > 20
        assert result["character"].hit_points.current <= 44

    def test_short_rest_cannot_exceed_max_hp(self):
        from app.api.routes.rest_routes import calculate_short_rest
        char = _make_character(hit_points=HitPoints(current=43, maximum=44), hit_dice_remaining=5)
        result = calculate_short_rest(char, hit_dice_to_spend=1)
        assert result["character"].hit_points.current <= 44

    def test_short_rest_cannot_spend_more_hit_dice_than_available(self):
        from app.api.routes.rest_routes import calculate_short_rest
        char = _make_character(hit_dice_remaining=1)
        result = calculate_short_rest(char, hit_dice_to_spend=3)
        assert result["hit_dice_remaining"] == 0
        # Should only spend what's available

    def test_short_rest_zero_hit_dice(self):
        from app.api.routes.rest_routes import calculate_short_rest
        char = _make_character(hit_dice_remaining=0)
        result = calculate_short_rest(char, hit_dice_to_spend=1)
        assert result["hp_recovered"] == 0
        assert result["hit_dice_remaining"] == 0

    def test_short_rest_warlock_recovers_spell_slots(self):
        from app.api.routes.rest_routes import calculate_short_rest
        char = _make_character(
            character_class=CharacterClass.WARLOCK,
            spellcasting=SpellCasting(
                spellcasting_ability="charisma",
                spell_slots=[SpellSlot(level=1, total=2, used=2)],
            ),
        )
        result = calculate_short_rest(char, hit_dice_to_spend=0)
        assert result["spell_slots_recovered"] == [1]


class TestLongRest:
    """Test long rest mechanics."""

    def test_long_rest_recovers_all_hp(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(hit_points=HitPoints(current=10, maximum=44))
        result = calculate_long_rest(char)
        assert result["character"].hit_points.current == 44

    def test_long_rest_recovers_all_spell_slots(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(
            spellcasting=SpellCasting(
                spellcasting_ability="intelligence",
                spell_slots=[
                    SpellSlot(level=1, total=4, used=3),
                    SpellSlot(level=2, total=3, used=2),
                ],
            ),
        )
        result = calculate_long_rest(char)
        for slot in result["character"].spellcasting.spell_slots:
            assert slot.used == 0

    def test_long_rest_recovers_half_hit_dice(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(level=6, hit_dice_remaining=0)
        result = calculate_long_rest(char)
        assert result["hit_dice_remaining"] == 3  # Half of 6

    def test_long_rest_recovers_minimum_one_hit_die(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(level=1, hit_dice_remaining=0)
        result = calculate_long_rest(char)
        assert result["hit_dice_remaining"] >= 1

    def test_long_rest_reduces_exhaustion(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(exhaustion_level=3)
        result = calculate_long_rest(char)
        assert result["exhaustion_level"] == 2

    def test_long_rest_exhaustion_does_not_go_below_zero(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(exhaustion_level=0)
        result = calculate_long_rest(char)
        assert result["exhaustion_level"] == 0

    def test_long_rest_hit_dice_cap_at_level(self):
        from app.api.routes.rest_routes import calculate_long_rest
        char = _make_character(level=4, hit_dice_remaining=3)
        result = calculate_long_rest(char)
        # 3 remaining + 2 recovered (half of 4) = 5, but capped at level 4
        assert result["hit_dice_remaining"] == 4
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/test_rest_mechanics.py -v --tb=short
```

Expected: FAIL — `rest_routes` module does not exist

### Task C4: Implement rest mechanics route

**Files:**
- Create: `backend/app/api/routes/rest_routes.py`
- Modify: `backend/app/api/routes/__init__.py`

- [ ] **Step 1: Create rest_routes.py**

```python
"""Rest mechanics routes — short and long rests for player recovery."""

import logging
import random
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.models.game_models import (
    CharacterClass,
    CharacterSheet,
    RestRequest,
    RestResponse,
    RestType,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rest"])

# Hit die sizes by class
HIT_DIE_SIZE: dict[CharacterClass, int] = {
    CharacterClass.BARBARIAN: 12,
    CharacterClass.FIGHTER: 10,
    CharacterClass.PALADIN: 10,
    CharacterClass.RANGER: 10,
    CharacterClass.MONK: 8,
    CharacterClass.CLERIC: 8,
    CharacterClass.DRUID: 8,
    CharacterClass.ROGUE: 8,
    CharacterClass.BARD: 8,
    CharacterClass.WARLOCK: 8,
    CharacterClass.WIZARD: 6,
    CharacterClass.SORCERER: 6,
}


def _get_hit_die_size(character_class: CharacterClass) -> int:
    """Return the hit die size for a character class."""
    return HIT_DIE_SIZE.get(character_class, 8)


def _con_modifier(abilities) -> int:
    """Calculate Constitution modifier."""
    return (abilities.constitution - 10) // 2


def calculate_short_rest(character: CharacterSheet, hit_dice_to_spend: int) -> dict[str, Any]:
    """Calculate the effects of a short rest.

    Args:
        character: The character taking a short rest.
        hit_dice_to_spend: Number of hit dice to spend for healing.

    Returns:
        Dict with hp_recovered, hit_dice_remaining, spell_slots_recovered, and updated character.
    """
    hit_dice_remaining = character.hit_dice_remaining if character.hit_dice_remaining is not None else character.level
    dice_to_spend = min(hit_dice_to_spend, hit_dice_remaining)

    die_size = _get_hit_die_size(character.character_class)
    con_mod = _con_modifier(character.abilities)

    hp_recovered = 0
    for _ in range(dice_to_spend):
        roll = random.randint(1, die_size) + con_mod
        hp_recovered += max(1, roll)  # Minimum 1 HP per die

    new_hp = min(character.hit_points.current + hp_recovered, character.hit_points.maximum)
    actual_recovered = new_hp - character.hit_points.current
    character.hit_points.current = new_hp
    character.hit_dice_remaining = hit_dice_remaining - dice_to_spend

    # Warlock: recover spell slots on short rest
    spell_slots_recovered: list[int] = []
    if character.character_class == CharacterClass.WARLOCK and character.spellcasting:
        for slot in character.spellcasting.spell_slots:
            if slot.used > 0:
                spell_slots_recovered.append(slot.level)
                slot.used = 0

    return {
        "hp_recovered": actual_recovered,
        "hit_dice_remaining": character.hit_dice_remaining,
        "spell_slots_recovered": spell_slots_recovered,
        "character": character,
    }


def calculate_long_rest(character: CharacterSheet) -> dict[str, Any]:
    """Calculate the effects of a long rest.

    Args:
        character: The character taking a long rest.

    Returns:
        Dict with hp_recovered, hit_dice_remaining, exhaustion_level, spell_slots_recovered, and updated character.
    """
    # Full HP recovery
    hp_recovered = character.hit_points.maximum - character.hit_points.current
    character.hit_points.current = character.hit_points.maximum

    # Recover all spell slots
    spell_slots_recovered: list[int] = []
    if character.spellcasting:
        for slot in character.spellcasting.spell_slots:
            if slot.used > 0:
                spell_slots_recovered.append(slot.level)
                slot.used = 0

    # Recover half of total hit dice (minimum 1)
    hit_dice_remaining = character.hit_dice_remaining if character.hit_dice_remaining is not None else 0
    dice_to_recover = max(1, character.level // 2)
    hit_dice_remaining = min(hit_dice_remaining + dice_to_recover, character.level)
    character.hit_dice_remaining = hit_dice_remaining

    # Reduce exhaustion by 1
    exhaustion_level = max(0, character.exhaustion_level - 1)
    character.exhaustion_level = exhaustion_level

    return {
        "hp_recovered": hp_recovered,
        "hit_dice_remaining": hit_dice_remaining,
        "exhaustion_level": exhaustion_level,
        "spell_slots_recovered": spell_slots_recovered,
        "character": character,
    }


@router.post("/game/rest", response_model=RestResponse)
async def perform_rest(request: RestRequest):
    """Perform a short or long rest for a character."""
    scribe = get_scribe()
    character_data = await scribe.get_character(request.character_id)

    if "error" in character_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {request.character_id} not found",
        )

    character = CharacterSheet(**character_data)

    if request.rest_type == RestType.SHORT:
        result = calculate_short_rest(character, request.hit_dice_to_spend)
    else:
        result = calculate_long_rest(character)

    # Persist the updated character
    await scribe.update_character(request.character_id, result["character"].model_dump())

    return RestResponse(
        success=True,
        message=f"{'Short' if request.rest_type == RestType.SHORT else 'Long'} rest completed.",
        hp_recovered=result["hp_recovered"],
        spell_slots_recovered=result.get("spell_slots_recovered", []),
        hit_dice_remaining=result["hit_dice_remaining"],
        exhaustion_level=result.get("exhaustion_level", character.exhaustion_level),
    )
```

- [ ] **Step 2: Register the router in __init__.py**

Add to `backend/app/api/routes/__init__.py`:

```python
from .rest_routes import router as rest_router
```

And add `rest_router` to `all_routers` list.

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/test_rest_mechanics.py -v --tb=short
```

Expected: All 12 tests pass

- [ ] **Step 4: Run full test suite to verify no regressions**

```bash
cd backend && uv run pytest tests/ -v --tb=short -q 2>&1 | tail -20
```

Expected: No new failures

- [ ] **Step 5: Commit backend**

```bash
git add backend/app/models/game_models.py backend/app/api/routes/rest_routes.py backend/app/api/routes/__init__.py backend/tests/test_rest_mechanics.py
git commit -m "feat: add short and long rest mechanics with hit dice tracking (closes #514)"
```

### Task C5: Add rest buttons to GameStateDisplay frontend

**Files:**
- Modify: `frontend/src/components/GameStateDisplay.tsx`
- Modify: `frontend/src/components/GameStateDisplay.module.css`

- [ ] **Step 1: Add rest buttons to GameStateDisplay.tsx**

Add a "Rest" section below the action form in GameStateDisplay. Add a `handleRest` function that POSTs to `/api/game/rest`. Show "Short Rest" and "Long Rest" buttons. Display hit dice available count.

- [ ] **Step 2: Add CSS styles for rest buttons**

Add `.restSection`, `.restButton`, `.restInfo` styles to `GameStateDisplay.module.css`.

- [ ] **Step 3: Verify frontend builds**

```bash
cd frontend && bun run build
```

Expected: Build succeeds

- [ ] **Step 4: Commit frontend**

```bash
git add frontend/src/components/GameStateDisplay.tsx frontend/src/components/GameStateDisplay.module.css
git commit -m "feat: add short/long rest buttons to GameStateDisplay"
```

### Task C6: Push and merge PR

- [ ] **Step 1: Push to PR branch**

```bash
git checkout copilot/add-short-and-long-rest-mechanics
git rebase main
git push origin copilot/add-short-and-long-rest-mechanics --force-with-lease
```

- [ ] **Step 2: Update PR and mark ready**

```bash
gh pr edit 514 --title "feat: add short and long rest mechanics for player recovery"
gh pr ready 514
```

- [ ] **Step 3: Merge PR**

```bash
gh pr merge 514 --squash --delete-branch
```

- [ ] **Step 4: Close issue**

```bash
gh issue close 514 -c "Fixed in PR #514"
```

---

## Execution Order

```
Workstream A (merge #533)
    |
    v
  main updated
   / \
  v   v
Workstream B (#474)   Workstream C (#514)
  (parallel)            (parallel)
   \ /
    v
  all merged, issues closed
```
