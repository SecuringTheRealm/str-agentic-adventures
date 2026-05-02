# Phase 1: Foundation Fixes - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the foundation bugs that block all other work - ability scores, character persistence, rest crashes, dead code, error handling patterns.

**Architecture:** Three parallel worktree-isolated agents each handling a domain: backend game logic, frontend components, and architecture/API cleanup. Each produces one PR.

**Tech Stack:** Python/FastAPI/SQLAlchemy (backend), React/TypeScript/CSS Modules (frontend), Pydantic models, pytest, vitest

---

## Agent 1: `backend-foundations`

### Task 1: Fix ability score reading in create_character (#608, #620)

**Files:**
- Modify: `backend/app/agents/scribe_agent.py:353-360`
- Test: `backend/tests/test_character_creation_abilities.py` (create)

- [ ] **Step 1: Write failing test for ability score passthrough**

Create `backend/tests/test_character_creation_abilities.py`:

```python
"""Tests for character creation ability score handling."""

import pytest

from app.agents.scribe_agent import ScribeAgent


@pytest.fixture
def scribe():
    return ScribeAgent()


@pytest.mark.asyncio
async def test_create_character_uses_provided_abilities(scribe):
    """Abilities from the nested 'abilities' dict should be used, not defaults."""
    character_data = {
        "name": "TestHero",
        "class": "fighter",
        "race": "human",
        "level": 1,
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8,
        },
    }
    result = await scribe.create_character(character_data)

    # Human gets +1 to all abilities
    assert result["abilities"]["strength"] == 17
    assert result["abilities"]["dexterity"] == 15
    assert result["abilities"]["constitution"] == 15
    assert result["abilities"]["intelligence"] == 11
    assert result["abilities"]["wisdom"] == 13
    assert result["abilities"]["charisma"] == 9


@pytest.mark.asyncio
async def test_create_character_defaults_when_no_abilities(scribe):
    """When no abilities dict provided, default to 10 for each."""
    character_data = {
        "name": "DefaultHero",
        "class": "wizard",
        "race": "elf",
        "level": 1,
    }
    result = await scribe.create_character(character_data)

    # Elf gets +2 DEX
    assert result["abilities"]["dexterity"] == 12
    # Others default to 10 + racial bonuses
    assert result["abilities"]["strength"] == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_character_creation_abilities.py -v`
Expected: FAIL - strength will be 11 (10 + 1 racial) instead of 17

- [ ] **Step 3: Fix ability score reading**

In `backend/app/agents/scribe_agent.py`, replace lines 352-360:

```python
            # Get base abilities from input
            base_abilities = {
                "strength": character_data.get("strength", 10),
                "dexterity": character_data.get("dexterity", 10),
                "constitution": character_data.get("constitution", 10),
                "intelligence": character_data.get("intelligence", 10),
                "wisdom": character_data.get("wisdom", 10),
                "charisma": character_data.get("charisma", 10),
            }
```

With:

```python
            # Get base abilities from nested abilities dict
            abilities_data = character_data.get("abilities", {})
            base_abilities = {
                "strength": abilities_data.get("strength", 10),
                "dexterity": abilities_data.get("dexterity", 10),
                "constitution": abilities_data.get("constitution", 10),
                "intelligence": abilities_data.get("intelligence", 10),
                "wisdom": abilities_data.get("wisdom", 10),
                "charisma": abilities_data.get("charisma", 10),
            }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest backend/tests/test_character_creation_abilities.py -v`
Expected: PASS

- [ ] **Step 5: Run full test suite to check for regressions**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass (1139+)

- [ ] **Step 6: Commit**

```bash
git add backend/app/agents/scribe_agent.py backend/tests/test_character_creation_abilities.py
git commit -m "fix: read ability scores from nested abilities dict (closes #608, closes #620)"
```

---

### Task 2: Fix rest endpoint crash (#612)

**Files:**
- Modify: `backend/app/api/routes/rest_routes.py:169`
- Test: `backend/tests/test_rest_endpoint_fix.py` (create)

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_rest_endpoint_fix.py`:

```python
"""Tests for rest endpoint character update call."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.routes.rest_routes import router


@pytest.mark.asyncio
async def test_rest_endpoint_calls_update_with_two_args():
    """update_character must be called with (character_id, updates) not just (character)."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/game")

    mock_scribe = AsyncMock()
    mock_scribe.get_character = AsyncMock(return_value={
        "id": "char_123",
        "name": "TestHero",
        "hit_points": {"current": 10, "maximum": 10},
        "hit_dice": "1d10",
        "hit_dice_remaining": 1,
        "level": 1,
        "character_class": "fighter",
        "abilities": {"constitution": 14},
        "spellcasting": None,
    })
    mock_scribe.update_character = AsyncMock(return_value={"success": True})

    with patch("app.api.routes.rest_routes.get_scribe", return_value=mock_scribe):
        client = TestClient(app)
        response = client.post("/game/game/rest", json={
            "character_id": "char_123",
            "rest_type": "long",
        })

    # Verify update_character was called with character_id AND updates dict
    if mock_scribe.update_character.called:
        args = mock_scribe.update_character.call_args
        assert len(args[0]) == 2, f"update_character should take 2 args, got {len(args[0])}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_rest_endpoint_fix.py -v`
Expected: FAIL or ERROR

- [ ] **Step 3: Fix the rest endpoint**

Read `backend/app/api/routes/rest_routes.py` to understand the full context, then fix line 169. The rest functions (`calculate_long_rest`, `calculate_short_rest`) expect a dict with hit_points etc. The result contains a `character` key. Fix the `update_character` call to pass both `character_id` and the updated character data:

Replace the `update_character` call (around line 169):

```python
await scribe.update_character(result["character"])
```

With:

```python
character_data = result["character"]
if hasattr(character_data, "model_dump"):
    character_data = character_data.model_dump()
await scribe.update_character(request.character_id, character_data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest backend/tests/test_rest_endpoint_fix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/routes/rest_routes.py backend/tests/test_rest_endpoint_fix.py
git commit -m "fix: pass character_id and updates to update_character in rest endpoint (closes #612)"
```

---

### Task 3: Fix DetachedInstanceError in update_character (#695)

**Files:**
- Modify: `backend/app/agents/scribe_agent.py:482-496`

- [ ] **Step 1: Read the current code**

Read `backend/app/agents/scribe_agent.py` lines 469-500 to understand the full `update_character` method.

- [ ] **Step 2: Fix the session context**

The bug is that `db_character.data = character` and `db.commit()` happen outside the `with get_session_context() as db:` block. Move the update logic inside:

Replace the buggy section (lines ~482-496):

```python
        try:
            with get_session_context() as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data

            # Apply updates (simplified for now)
            for key, value in updates.items():
                if key in character and key != "id":
                    character[key] = value

                db_character.data = character
                db.commit()
            return character
```

With:

```python
        try:
            with get_session_context() as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data

                # Apply updates inside session context
                for key, value in updates.items():
                    if key in character and key != "id":
                        character[key] = value

                db_character.data = character
                db.commit()
            return character
```

- [ ] **Step 3: Run existing tests**

Run: `uv run pytest backend/tests/ -v --tb=short -k "character or save or auto_save"`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/agents/scribe_agent.py
git commit -m "fix: move db.commit() inside session context to prevent DetachedInstanceError (closes #695)"
```

---

### Task 4: Replace hash() with uuid4 for IDs (#656)

**Files:**
- Modify: `backend/app/api/routes/session_routes.py:195`
- Modify: `backend/app/api/routes/combat_routes.py:68`

- [ ] **Step 1: Fix session_routes.py**

In `backend/app/api/routes/session_routes.py`, add import at top:

```python
import uuid
```

Replace line 195:

```python
"session_id": f"session_{campaign_id}_{hash(str(character_ids))}",
```

With:

```python
"session_id": f"session_{campaign_id}_{uuid.uuid4().hex[:8]}",
```

- [ ] **Step 2: Fix combat_routes.py**

In `backend/app/api/routes/combat_routes.py`, add import at top:

```python
import uuid
```

Replace line 68:

```python
"combat_id": f"combat_{session_id}_{hash(str(participants))}",
```

With:

```python
"combat_id": f"combat_{session_id}_{uuid.uuid4().hex[:8]}",
```

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/routes/session_routes.py backend/app/api/routes/combat_routes.py
git commit -m "fix: replace Python hash() with uuid4 for session and combat IDs (closes #656)"
```

---

### Task 5: Remove duplicate character_id from request models (#607, #621)

**Files:**
- Modify: `backend/app/models/game_models.py:556-576`
- Modify: `backend/app/api/routes/spell_routes.py`

- [ ] **Step 1: Remove character_id from ManageSpellsRequest**

In `backend/app/models/game_models.py`, change `ManageSpellsRequest` (line 556):

From:

```python
class ManageSpellsRequest(BaseModel):
    character_id: str
    action: Literal["learn", "forget", "prepare", "unprepare"]
    spell_ids: list[str]
```

To:

```python
class ManageSpellsRequest(BaseModel):
    action: Literal["learn", "forget", "prepare", "unprepare"]
    spell_ids: list[str]
```

- [ ] **Step 2: Remove character_id from ManageSpellSlotsRequest**

Change `ManageSpellSlotsRequest` (line 562):

From:

```python
class ManageSpellSlotsRequest(BaseModel):
    character_id: str
    action: Literal["use", "recover", "set"]
    slot_level: int
    count: int | None = 1
```

To:

```python
class ManageSpellSlotsRequest(BaseModel):
    action: Literal["use", "recover", "set"]
    slot_level: int
    count: int | None = 1
```

- [ ] **Step 3: Remove combat_id from CastSpellRequest**

Change `CastSpellRequest` (line 569):

From:

```python
class CastSpellRequest(BaseModel):
    combat_id: str
    character_id: str
    spell_id: str
    slot_level: int
    target_ids: list[str] | None = Field(default_factory=list)
    spell_attack_roll: int | None = None
```

To:

```python
class CastSpellRequest(BaseModel):
    character_id: str
    spell_id: str
    slot_level: int
    target_ids: list[str] | None = Field(default_factory=list)
    spell_attack_roll: int | None = None
```

- [ ] **Step 4: Update route handlers to use path params**

In `backend/app/api/routes/spell_routes.py`, update any references to `request.character_id` or `request.combat_id` to use the path parameter instead. Read the file first to find exact usages.

- [ ] **Step 5: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass (may need to update test request bodies)

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/game_models.py backend/app/api/routes/spell_routes.py
git commit -m "fix: remove duplicate character_id/combat_id from request bodies (closes #607, closes #621)"
```

---

### Task 6: Add proper validation to dice roll endpoint (#624)

**Files:**
- Modify: `backend/app/api/routes/dice_routes.py:15-43`
- Modify: `backend/app/models/game_models.py` (add model)

- [ ] **Step 1: Add DiceRollRequest model**

In `backend/app/models/game_models.py`, add:

```python
class DiceRollRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    notation: str = Field(default="1d20", description="D&D dice notation (e.g., '1d20', '2d6+3')")
```

- [ ] **Step 2: Update dice roll endpoint**

In `backend/app/api/routes/dice_routes.py`, replace the `roll_dice` function signature:

From:

```python
@router.post("/dice/roll", response_model=dict[str, Any])
async def roll_dice(dice_data: dict[str, str]) -> dict[str, Any]:
```

To:

```python
from app.models.game_models import DiceRollRequest

@router.post("/dice/roll", response_model=dict[str, Any])
async def roll_dice(request: DiceRollRequest) -> dict[str, Any]:
```

And update references from `dice_data.get("notation", "1d20")` to `request.notation`.

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/game_models.py backend/app/api/routes/dice_routes.py
git commit -m "fix: add DiceRollRequest model with extra=forbid to reject unknown fields (closes #624)"
```

---

## Agent 2: `frontend-foundations`

### Task 7: Add missing CSS module classes for CharacterSheet (#666)

**Files:**
- Modify: `frontend/src/components/CharacterSheet.module.css`

- [ ] **Step 1: Read current CSS file**

Read `frontend/src/components/CharacterSheet.module.css` to understand existing patterns and theme variables.

- [ ] **Step 2: Add all 27 missing CSS class definitions**

Append to `frontend/src/components/CharacterSheet.module.css`. The classes must match the theme (dark fantasy, teal/gold accents, `var(--color-*)` variables). Group by section:

```css
/* === Equipment Section === */
.equipmentSlots {
  margin-bottom: 1rem;
}

.equipmentGrid {
  display: grid;
  gap: 0.25rem;
}

.equipmentSlot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.slotLabel {
  color: var(--color-accent-gold, #c8a96e);
  font-weight: 600;
  min-width: 5rem;
}

/* === Inventory Items === */
.inventoryHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.inventoryItems {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.itemWeight {
  color: var(--color-text-muted, #8a8a8a);
  font-size: 0.75rem;
}

.itemValue {
  color: var(--color-accent-gold, #c8a96e);
  font-size: 0.75rem;
}

.magicalIndicator {
  color: var(--color-accent-teal, #4ecdc4);
  font-size: 0.7rem;
  font-style: italic;
}

/* === Level === */
.levelLabel {
  font-size: 0.85rem;
  color: var(--color-text-muted, #8a8a8a);
}

/* === Spell Section === */
.spellSlots {
  margin-bottom: 1rem;
}

.spellSlotGrid {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.spellSlotLevel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.slotIndicators {
  display: flex;
  gap: 0.25rem;
}

.slotCount {
  font-size: 0.75rem;
  color: var(--color-text-muted, #8a8a8a);
}

.spellStats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.spellStat {
  font-size: 0.85rem;
}

.spellManagement {
  margin-top: 0.5rem;
}

.spellList {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.spellLevelGroup {
  margin-bottom: 0.5rem;
}

.spellItem {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
  font-size: 0.85rem;
}

.spellName {
  font-weight: 500;
}

.spellSchool {
  font-size: 0.75rem;
  color: var(--color-text-muted, #8a8a8a);
  font-style: italic;
}

.spellRange {
  font-size: 0.75rem;
  color: var(--color-text-muted, #8a8a8a);
}

.spellCastingTime {
  font-size: 0.75rem;
  color: var(--color-text-muted, #8a8a8a);
}

.castButton {
  background: var(--color-accent-teal, #4ecdc4);
  color: var(--color-fantasy-primary, #1a1a2e);
  border: none;
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
}

.castButton:hover {
  opacity: 0.85;
}

.cantrips {
  margin-bottom: 0.5rem;
}

.preparedSpells {
  margin-bottom: 0.5rem;
}

.concentrationIndicator {
  color: var(--color-accent-gold, #c8a96e);
  font-size: 0.7rem;
}

.ritualIndicator {
  color: var(--color-accent-teal, #4ecdc4);
  font-size: 0.7rem;
}
```

- [ ] **Step 3: Run frontend tests**

Run: `cd frontend && bun test:run`
Expected: All 236 tests pass

- [ ] **Step 4: Verify visually in browser**

Navigate to a game page and check the character sheet sidebar renders properly.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/CharacterSheet.module.css
git commit -m "fix: add 27 missing CSS module class definitions for CharacterSheet (closes #666)"
```

---

### Task 8: Fix character sheet overflow (#615)

**Files:**
- Modify: `frontend/src/components/CharacterSheet.module.css`
- Modify: `frontend/src/components/GameInterface.module.css`

Note: CharacterSheet itself already has `overflow-y: auto`. The overflow issue is in the parent layout container in GameInterface.

- [ ] **Step 1: Read GameInterface CSS**

Read `frontend/src/components/GameInterface.module.css` to find the sidebar container that wraps CharacterSheet.

- [ ] **Step 2: Fix the parent container**

The sidebar container needs `overflow: hidden` and the character sheet area needs constrained height. Add or modify the sidebar CSS to ensure the character sheet scrolls within its allotted space:

```css
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
}
```

Ensure the CharacterSheet wrapper has:

```css
flex: 1;
min-height: 0;
overflow-y: auto;
```

- [ ] **Step 3: Run frontend tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/GameInterface.module.css frontend/src/components/CharacterSheet.module.css
git commit -m "fix: constrain character sheet sidebar height to prevent viewport overflow (closes #615)"
```

---

### Task 9: Delete dead components (#664)

**Files:**
- Delete: `frontend/src/components/GameStateDisplay.tsx`
- Delete: `frontend/src/components/GameStateDisplay.module.css`

Note: Research confirmed only `GameStateDisplay.tsx` is truly dead (no imports). `CampaignCreation.tsx` and `PlayerList.tsx` have test files that import them, so they stay.

- [ ] **Step 1: Verify no imports exist**

Run: `rg "GameStateDisplay" frontend/src/ --type ts --type tsx`
Expected: Only the file itself and possibly its CSS module

- [ ] **Step 2: Delete the files**

```bash
rm frontend/src/components/GameStateDisplay.tsx
rm frontend/src/components/GameStateDisplay.module.css 2>/dev/null
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove dead GameStateDisplay component (closes #664)"
```

---

### Task 10: Fix error handling for openapi-fetch (#665)

**Files:**
- Modify: `frontend/src/components/CampaignGallery.tsx:64-75`

- [ ] **Step 1: Read the current error handling code**

Read `frontend/src/components/CampaignGallery.tsx` lines 40-80.

- [ ] **Step 2: Replace axios-style error parsing**

Replace the `if (err.response)` / `else if (err.request)` block with openapi-fetch compatible error handling:

```typescript
if (err instanceof Error) {
  errorMessage = err.message || "Failed to load templates";
} else if (typeof err === "object" && err !== null) {
  errorMessage = (err as { detail?: string }).detail || "Failed to load templates";
}
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/CampaignGallery.tsx
git commit -m "fix: replace dead axios error handling with openapi-fetch pattern (closes #665)"
```

---

### Task 11: Fix CampaignSelection type bug (#676)

**Files:**
- Modify: `frontend/src/components/CampaignSelection.tsx:33`

- [ ] **Step 1: Fix the type access**

In `frontend/src/components/CampaignSelection.tsx`, line 33 accesses `data.campaigns` but `getCampaigns()` returns `Campaign[]` directly.

Change:

```typescript
const data = await getCampaigns();
setCampaigns(data.campaigns);
```

To:

```typescript
const data = await getCampaigns();
setCampaigns(data);
```

- [ ] **Step 2: Run tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CampaignSelection.tsx
git commit -m "fix: use getCampaigns() return value directly, not .campaigns property (closes #676)"
```

---

### Task 12: Add null safety for hit_points and setting (#682, #683)

**Files:**
- Modify: `frontend/src/components/CharacterSheet.tsx:208`
- Modify: `frontend/src/components/MobileGameLayout.tsx:73-74`
- Modify: `frontend/src/components/CampaignGallery.tsx:227`

- [ ] **Step 1: Fix CharacterSheet hit_points access**

In `frontend/src/components/CharacterSheet.tsx` line 208, change:

```typescript
{character.hit_points.current} / {character.hit_points.maximum}
```

To:

```typescript
{character.hit_points?.current ?? 0} / {character.hit_points?.maximum ?? 0}
```

- [ ] **Step 2: Fix MobileGameLayout hit_points access**

In `frontend/src/components/MobileGameLayout.tsx` lines 73-74, change:

```typescript
currentHp={character.hit_points.current}
maxHp={character.hit_points.maximum}
```

To:

```typescript
currentHp={character.hit_points?.current ?? 0}
maxHp={character.hit_points?.maximum ?? 0}
```

- [ ] **Step 3: Fix CampaignGallery setting substring**

In `frontend/src/components/CampaignGallery.tsx` line 227, change:

```typescript
<span>{template.setting.substring(0, 100)}...</span>
```

To:

```typescript
<span>{template.setting?.substring(0, 100) ?? "No setting available"}...</span>
```

- [ ] **Step 4: Run tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/CharacterSheet.tsx frontend/src/components/MobileGameLayout.tsx frontend/src/components/CampaignGallery.tsx
git commit -m "fix: add null safety for hit_points and setting access (closes #682, closes #683)"
```

---

## Agent 3: `arch-cleanup`

### Task 13: Delete dead routers/ directory (#657)

**Files:**
- Delete: `backend/app/routers/` (entire directory)

- [ ] **Step 1: Verify no imports**

Run: `rg "from app.routers" backend/ --type py`
Run: `rg "from app.routers" backend/tests/ --type py`
Expected: No matches

- [ ] **Step 2: Delete the directory**

```bash
rm -rf backend/app/routers/
```

- [ ] **Step 3: Run all tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All 1139+ pass

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove dead legacy routers/ directory (closes #657)"
```

---

### Task 14: Fix HTTP 200 + success=false anti-pattern (#654)

**Files:**
- Modify: `backend/app/api/routes/npc_routes.py:165-170, 262-267`
- Modify: `backend/app/api/routes/spell_routes.py:112-115, 471-474`
- Modify: `backend/app/api/routes/character_routes.py:223-225`
- Modify: `backend/app/api/routes/item_routes.py:69-75`
- Modify: `backend/app/api/routes/ai_routes.py:140-145`

- [ ] **Step 1: Fix npc_routes.py (2 locations)**

In `backend/app/api/routes/npc_routes.py`, replace both exception handlers.

Location 1 (~line 165):

```python
    except Exception as e:
        return NPCInteractionResponse(
            success=False,
            message=f"Failed to log NPC interaction: {str(e)}",
            interaction_id="",
        )
```

Replace with:

```python
    except Exception as e:
        logger.error("Failed to log NPC interaction: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log NPC interaction",
        ) from e
```

Location 2 (~line 262):

```python
    except Exception as e:
        return NPCStatsResponse(
            success=False,
            message=f"Failed to generate NPC stats: {str(e)}",
            generated_stats={},
        )
```

Replace with:

```python
    except Exception as e:
        logger.error("Failed to generate NPC stats: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate NPC stats",
        ) from e
```

- [ ] **Step 2: Fix spell_routes.py (2 locations)**

Apply the same pattern to `backend/app/api/routes/spell_routes.py` at lines ~112 and ~471. Replace `return ...Response(success=False, ...)` with `raise HTTPException(status_code=500, detail=...)`.

- [ ] **Step 3: Fix character_routes.py, item_routes.py, ai_routes.py**

Apply the same pattern to each. Read each file to find the exact exception handler, then replace the return with raise HTTPException.

- [ ] **Step 4: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: Some tests may need updating if they assert on `success=False` responses. Fix those tests to expect 500 status codes.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/routes/npc_routes.py backend/app/api/routes/spell_routes.py backend/app/api/routes/character_routes.py backend/app/api/routes/item_routes.py backend/app/api/routes/ai_routes.py
git commit -m "fix: replace HTTP 200 + success=false with proper 500 error responses (closes #654)"
```

---

### Task 15: Add fallback indicator to stub endpoints (#653)

**Files:**
- Modify: `backend/app/api/routes/character_routes.py` (encumbrance endpoint)
- Modify: `backend/app/api/routes/spell_routes.py` (spells, spell-slots endpoints)

- [ ] **Step 1: Add X-Fallback header to encumbrance endpoint**

In the encumbrance endpoint (`GET /character/{id}/encumbrance`), add a response header indicating the data is a stub:

```python
from fastapi.responses import JSONResponse

@router.get("/character/{character_id}/encumbrance", response_model=EncumbranceResponse)
async def get_encumbrance(character_id: str) -> JSONResponse:
    # ... existing stub logic ...
    response = JSONResponse(content=result)
    response.headers["X-Fallback"] = "true"
    response.headers["X-Fallback-Reason"] = "Encumbrance calculation uses placeholder values"
    return response
```

- [ ] **Step 2: Add stub warnings to spell endpoints**

Add similar headers to the `POST /character/{id}/spells` and `POST /character/{id}/spell-slots` endpoints.

- [ ] **Step 3: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/routes/character_routes.py backend/app/api/routes/spell_routes.py
git commit -m "fix: add X-Fallback header to stub endpoints (closes #653)"
```

---

### Task 16: Fix POST endpoints to return 201 (#640)

**Files:**
- Modify: `backend/app/api/routes/campaign_routes.py`
- Modify: `backend/app/api/routes/character_routes.py`
- Modify: `backend/app/api/routes/spell_routes.py`
- Modify: `backend/app/api/routes/inventory_routes.py`
- Modify: `backend/app/api/routes/item_routes.py`

- [ ] **Step 1: Add status_code=201 to creation endpoints**

For each POST endpoint that creates a resource, add `status_code=status.HTTP_201_CREATED` to the decorator. The endpoints are:

- `POST /campaign` in campaign_routes.py
- `POST /campaign/clone` in campaign_routes.py
- `POST /character` in character_routes.py
- `POST /inventory/{id}/add` in inventory_routes.py

Note: `POST /character/{id}/level-up`, `POST /character/{id}/award-experience`, `POST /character/{id}/spells`, `POST /character/{id}/spell-slots`, `POST /character/{id}/equipment` are action endpoints (not creation), so they should stay at 200.

Example fix for campaign creation:

```python
@router.post("/campaign", response_model=Campaign, status_code=status.HTTP_201_CREATED)
```

- [ ] **Step 2: Run tests and fix assertions**

Run: `uv run pytest backend/tests/ -v --tb=short`
Some tests may assert `response.status_code == 200` for creation endpoints. Update those to `201`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/routes/campaign_routes.py backend/app/api/routes/character_routes.py backend/app/api/routes/inventory_routes.py
git commit -m "fix: return 201 for resource creation endpoints (closes #640)"
```

---

### Task 17: Fix award-experience schema and generate-image validation (#638, #639)

**Files:**
- Modify: `backend/app/api/routes/character_routes.py:115-118`
- Modify: `backend/app/models/game_models.py` (add model)
- Modify: `backend/app/api/routes/ai_routes.py:148-175`

- [ ] **Step 1: Add AwardExperienceRequest model**

In `backend/app/models/game_models.py`, add:

```python
class AwardExperienceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    experience_points: int = Field(..., gt=0, description="Experience points to award")
```

- [ ] **Step 2: Update award-experience endpoint**

In `backend/app/api/routes/character_routes.py`, change:

```python
async def award_experience(character_id: str, experience_data: dict[str, int]) -> dict[str, Any]:
```

To:

```python
async def award_experience(character_id: str, request: AwardExperienceRequest) -> dict[str, Any]:
```

And update the body to use `request.experience_points` instead of `experience_data.get("experience_points", 0)`.

- [ ] **Step 3: Add GenerateImageRequest model**

In `backend/app/models/game_models.py`, add:

```python
class GenerateImageRequest(BaseModel):
    image_type: Literal["character_portrait", "scene_illustration", "item_visualization"]
    details: dict[str, Any] = Field(default_factory=dict)
```

- [ ] **Step 4: Update generate-image endpoint**

In `backend/app/api/routes/ai_routes.py`, change:

```python
async def generate_image(request: Request, image_request: dict[str, Any]) -> dict[str, Any]:
```

To:

```python
async def generate_image(request: Request, image_request: GenerateImageRequest) -> dict[str, Any]:
```

And update body to use `image_request.image_type` and `image_request.details`.

- [ ] **Step 5: Run tests**

Run: `uv run pytest backend/tests/ -v --tb=short`
Expected: All pass (update tests that send raw dicts)

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/game_models.py backend/app/api/routes/character_routes.py backend/app/api/routes/ai_routes.py
git commit -m "fix: add proper Pydantic models for award-experience and generate-image (closes #638, closes #639)"
```

---

## Final Verification

After all three agents complete:

- [ ] **Run full backend test suite**: `uv run pytest backend/tests/ -v`
- [ ] **Run full frontend test suite**: `cd frontend && bun test:run`
- [ ] **Run biome lint**: `cd frontend && bunx biome check --write .`
- [ ] **Run ruff lint**: `uv run ruff check backend/ --fix`
- [ ] **Create PRs**: One PR per agent branch
