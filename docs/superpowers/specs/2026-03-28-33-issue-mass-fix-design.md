# 33-Issue Mass Fix Design Spec

## Overview
Fix 33 open GitHub issues (all except #622, #587, #591, #404, #407, #567) grouped into 10 workstreams by system layer for maximum parallelism.

## Workstreams

### WS1: Combat Engine (#706, #707, #708, #711, #718)
**Root cause chain:** `start_combat()` never called -> encounters stay 'ready' -> `encounter_id='auto'` -> actions fail -> turns return empty.

**Fixes:**
- Wire `start_combat()` into `initialize_combat()` in combat_routes.py
- Generate combat IDs from UUID, not `combat_{None}_{hash}`
- Replace hardcoded `process_combat_action`/`process_exploration_action` stubs in session_routes.py with real agent delegation
- Populate initiative_order from character data via ScribeAgent
- Make `/combat/{id}/turn` flow through active combat state correctly

**Files:** `combat_routes.py`, `combat_mc_agent.py`, `session_routes.py`, `game_context_service.py`

### WS2: Session & World Gen (#709, #710, #722, #723)
**Problem:** Four endpoints return hardcoded text.

**Fixes:**
- #709: Persist session to DB via SessionManager, use uuid4 for IDs, wire `generate_opening_scene` to narrator
- #710: Replace 7 stub functions with narrator/DM agent calls; fallback uses campaign-specific data (name, setting, tone)
- #722: Pass full campaign context to narrator for opening narrative; fallback templates use campaign fields
- #723: Expand DM fallback keyword routing (explore, cast, talk, investigate, rest, sneak, search, trade, pray, craft); remove `[AI model not configured]` prefix (fixes #719 too)

**Files:** `session_routes.py`, `dungeon_master_agent.py`, `narrator_agent.py`

### WS3: API Contract Fixes (#713, #715, #717, #721, #603, #606)
**Problem:** Frontend/backend field name and type mismatches.

**Fixes:**
- #713: Fix `AIAssistanceRequest` TS interface: `prompt`->`text`, `context`->`context_type`
- #715: Accept both string and dict for `environment` in `StructuredMapRequest` (validator)
- #717: Remove duplicate path params from body; add spell name->ID lookup
- #721: Accept `item_name` as alias for `name`; make `item_type` optional with default "misc"
- #603: Accept `homebrew_rules` as string or list (validator coerces string to single-item list)
- #606: Change spell save DC to GET endpoint (or accept body on POST)

**Files:** `frontend/src/services/api.ts`, `inventory_routes.py`, `map_routes.py`, `combat_routes.py`, `campaign_routes.py`, `spell_routes.py`, `game_models.py`

### WS4: Game Mechanics (#716, #719, #720, #604)
**Fixes:**
- #716: Change `.attribute` to `['key']` dict access in rest_routes.py
- #719: Remove leaked prefix (handled in WS2 with #723)
- #720: Wire `encounter_xp` input into calculation in `award_xp()`
- #604: Preserve user-provided ability scores during character creation

**Files:** `rest_routes.py`, `combat_routes.py`, `character_routes.py`

### WS5: Persistence & Fallback (#712, #714, #605)
**Fixes:**
- #712: Persist NarrativeGenerationPlugin state to DB (JSON column on campaign or new table)
- #714: Better error messages, document env var requirements, improve health endpoint info
- #605: Generate basic deterministic battle map in fallback (simple grid with terrain types)

**Files:** `narrative_generation_plugin.py`, `narrator_agent.py`, `combat_cartographer_agent.py`, `azure_openai_client.py`, `db_models.py`

### WS6: shadcn/UI Migration (#418, #598, #599, #600)
**Scope:**
- #418: Complete shadcn/ui adoption, WCAG accessibility improvements, add routing guards
- #598: Campaign card visual polish with tone-driven colour mapping
- #599: Character creation/selection flow migration to shadcn
- #600: Campaign editor shadcn migration

**Approach:** Migrate remaining custom components to shadcn equivalents. Add tone->colour mapping for campaign cards. Ensure WCAG contrast ratios.

### WS7: Game Screen Polish (#589, #601)
**Scope:**
- #589: UI/UX polish across all pages
- #601: Game screen polish - CharacterSheet, DiceRoller, visuals

**Approach:** Visual refinements to game interface components. Better spacing, typography, colour consistency.

### WS8: Battle Maps (#419)
**Scope:** Replace DALL-E battle maps with interactive tile-based rendering.

**Approach:** Enhance existing TileGridRenderer with click-to-move, token drag, measurement tools. The canvas renderer already exists; add interactivity layer.

### WS9: Voice/Realtime (#588, #590, #592, #593, #594, #595)
**Scope:** Real-time voice DM with speech-to-speech.

**Approach:**
- #590: Backend token endpoint for WebRTC auth (already partially implemented in useRealtimeVoice)
- #592: WebRTC voice client in React (build on existing hook)
- #593: Simultaneous TTS + text streaming in ChatBox
- #594: DM voice personality and NPC voice differentiation
- #595: Multiplayer voice session with floor management
- #588: Integration of all voice components

### WS10: Multiplayer & Mobile (#511, #512)
**Scope:**
- #511: WebSocket session management foundations (build on existing websocketClient.ts)
- #512: Mobile-first responsive redesign (build on existing MobileGameLayout)

## Execution Strategy
- WS1-WS5 (bugs): Run in parallel worktree agents, each with backend context
- WS6-WS7 (UI): Run in parallel worktree agents with frontend context
- WS8-WS10 (features): Run after bugs are merged to avoid conflicts
- Each agent gets: backend agent, frontend agent, tester, UX reviewer, devil's advocate

## Dependencies
- WS2 partially fixes #719 (handled via WS4/WS2 overlap)
- WS1 must complete before WS8 (battle maps depend on working combat)
- WS6 should complete before WS7 (polish builds on migrated components)
- WS9 depends on working session management (WS2)

## Out of Scope
- #622 (assigned to external contributor)
- #587, #591 (need Azure AI Foundry infra deployment)
- #404 (diarization research)
- #407 (FLUX investigation)
- #567 (meta tracking issue)
