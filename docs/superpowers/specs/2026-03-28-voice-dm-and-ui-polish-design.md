# Voice DM & UI/UX Polish — Design Spec

## Overview

Two complementary workstreams that transform Secure the Realm from a functional AI D&D prototype into a lovable, immersive experience:

1. **Voice DM** — real-time speech-to-speech via Azure AI Foundry's GPT Realtime API, with multiplayer floor management
2. **UI/UX Polish** — fix critical bugs, migrate to shadcn/ui consistently, add emotional design moments

GitHub tracking: #588 (Voice), #589 (UI/UX), with sub-issues #590–#601.

---

## Part 1: Voice DM

### Interaction Model: Hybrid Campfire

The DM speaks, then yields the floor. Players talk freely among themselves. The DM responds when:
- A player addresses the DM directly (push-to-talk mic button, @DM keyword, or text input)
- A player clicks the "DM wants to speak" indicator (smart interrupt for game-critical moments)

This respects multiplayer roleplay — the AI never talks over players deliberating.

### Architecture

```
Player A (voice) ──WebRTC──► Azure Foundry (gpt-realtime-mini)
Player B (voice) ──WebRTC──► Same realtime session
Player C (text)  ──WebSocket──► FastAPI backend ──► Same AI context

DM responds ──► Voice to WebRTC-connected players
             ──► Text transcript to all players via WebSocket
```

**Auth flow:**
1. Browser calls `GET /api/realtime-token` on FastAPI backend
2. Backend uses Managed Identity to mint an ephemeral token (60s TTL) from the Foundry resource
3. Browser establishes WebRTC connection directly to `wss://{foundry}.openai.azure.com/openai/v1/realtime`
4. Audio travels browser ↔ Azure; JSON events on the data channel
5. Backend never handles audio — only game state sync and text player messages

### Model & Voice

| Setting | Value | Rationale |
|---|---|---|
| Model | `gpt-realtime-mini` (2025-12-15) | Cost-effective (~$1/hr), sufficient quality for D&D narration |
| Region | Sweden Central | Already deployed; supports realtime models |
| DM voice | `ballad` | Deep, resonant, storyteller quality |
| Combat voice | `echo` | Shift to urgent energy via session.update |
| VAD | `semantic_vad` | Detects utterance completion, not just silence |
| Interruption | `interrupt_response: true` | Players can cut in naturally |
| Latency | ~500ms typical | Natural "DM thinking" pause |

### Floor Management Protocol

**DM Turn:**
1. Player sends action (voice or text)
2. DM narrates response (voice streams + text streams simultaneously)
3. DM finishes → emits `response.done` → UI shows "DM is listening"
4. Mic buttons re-activate for all players

**Player Roleplay Phase:**
1. Players discuss among themselves (DM audio is muted/paused)
2. DM continues to receive audio context via WebRTC (for awareness)
3. If DM detects game-critical trigger → "✋ DM has something to say" card appears in side panel
4. Player clicks card → DM gets floor back and speaks
5. Or: any player holds push-to-talk → treated as addressing DM → DM responds

**Implementation:** Floor state is managed client-side via a React context (`VoiceSessionContext`). States: `dm_speaking`, `players_turn`, `dm_wants_floor`. The backend WebSocket broadcasts floor state changes to all connected clients.

### Frontend Voice Components

**New files:**
- `frontend/src/hooks/useRealtimeVoice.ts` — WebRTC connection lifecycle, audio stream management, VAD events
- `frontend/src/hooks/useFloorManager.ts` — floor state machine, "DM wants to speak" detection
- `frontend/src/components/VoiceMicButton.tsx` — push-to-talk with waveform visualiser
- `frontend/src/components/VoiceIndicator.tsx` — "DM is speaking" bar with audio waveform
- `frontend/src/components/FloorRequestCard.tsx` — "DM wants to speak" interactive card
- `frontend/src/components/VoiceControls.tsx` — volume slider, voice on/off toggle, voice selection
- `frontend/src/contexts/VoiceSessionContext.tsx` — shared state for voice session across components

**Modified files:**
- `ChatBox.tsx` — add VoiceMicButton to input bar, VoiceIndicator above messages, speaker icons on voiced messages
- `GameInterface.tsx` — add FloorRequestCard to side panel, VoiceControls below chat
- `GamePage.tsx` — wrap in VoiceSessionContext provider

### Backend Voice Endpoints

**New file:** `backend/app/api/routes/realtime.py`

- `GET /api/realtime-token` — mint ephemeral WebRTC token via Managed Identity
- `POST /api/realtime/session-config` — return DM system prompt + game state for realtime session initialisation

**Modified:** `backend/app/api/websocket_routes.py` — add floor management events (`floor_state_change`, `dm_wants_floor`, `dm_floor_granted`)

### Infrastructure

**Modified:** `infra/modules/ai-foundry.bicep` — add `gpt-realtime-mini` deployment:
```bicep
resource realtimeDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-realtime-mini'
  sku: { name: 'GlobalStandard', capacity: 1 }
  properties: {
    model: { format: 'OpenAI', name: 'gpt-realtime-mini', version: '2025-12-15' }
  }
}
```

### Cost Controls

- Voice sessions are opt-in (toggle, default off)
- Backend tracks voice minutes per session via token endpoint calls
- Configurable `max_voice_minutes_per_session` setting (default: 30)
- Voice auto-pauses after 2 minutes of silence (no player audio detected)

---

## Part 2: UI/UX Polish

### Critical Fixes (Must ship before any new features)

1. **Unstyled loading/error states** — `loading-state` and `error-message` CSS classes referenced in CampaignSelectionPage, GamePage, CharacterSelectionPage, CharacterNewPage are never defined. Create a shared `LoadingState` and `ErrorState` component using shadcn patterns.

2. **Light-on-dark error colours** — CampaignGallery error state uses `#f5f5f5` and `#fff5f5` backgrounds that look broken on the dark theme. Replace with theme-aware colours using `--color-bg-surface-dark`.

3. **Markdown in ChatBox** — DM LLM responses contain markdown (bold, italic, paragraphs) that render as raw asterisks. Add `react-markdown` with minimal styling.

4. **`alert()` in DiceRoller** — Replace with inline error message or toast component.

5. **CharacterSheet type escapes** — 15+ `(character as any)` casts mean equipment/spell sections always show empty. Extend the `Character` TypeScript type to include these fields.

6. **Pre-defined character flow** — `PredefinedCharacters` creates a fake client-side ID that fails when `GamePage` calls `getCharacter()`. Fix by actually POSTing the character to the backend first.

7. **Duplicate JSX in CampaignSelection** — campaign list rendering duplicated in two `viewMode` branches. Extract to shared component or use shadcn `Tabs`.

### Component Migration

Migrate all pages to consistent shadcn/ui usage:

| Page | Current State | Target |
|---|---|---|
| Campaign Hub | ✅ Uses Card, Badge, Button | Add Skeleton, Tabs, Tooltip, Toast |
| Campaign Editor | ❌ Raw HTML elements | Migrate to Input, Textarea, Select, Label, Button, Dialog, Switch |
| Character Selection | ❌ Raw divs and buttons | Migrate to Card, Button |
| Character Creation | ✅ Already uses shadcn | Add Progress, Slider, Tooltip, Alert |
| Pre-Defined Characters | ❌ Raw elements | Migrate to Card, Button |
| Game Interface | ⚠️ Partial | Migrate visual buttons to Button, add ScrollArea |
| DiceRoller | ⚠️ Partial | Fix palette, replace alert(), unify with fantasy theme |
| CharacterSheet | ❌ Plain headings | Add Card sections, Progress for HP, pip components for spells |

### New shadcn/ui Components to Install

`Tooltip`, `Sheet`, `Skeleton`, `Tabs`, `Progress`, `Separator`, `Switch`, `Alert`, `Dialog`, `Popover`, `ScrollArea`, `Toast`/`Sonner`

### Visual Design Direction

**Tone-driven campaign cards:** Each campaign's `tone` field drives the card colour scheme:
- `heroic` → gold borders, warm parchment tones
- `dark` → deep purple borders, candlelight amber accents
- `mysterious` → deep blue borders, silver highlights
- `lighthearted` → warm orange, cheerful palette
- `gritty` → dark grey, muted red accents

**DM message styling:** Replace plain chat bubbles with a parchment/scroll aesthetic — subtle texture background, serif font for narrative text, gold border-left accent. Player messages remain modern/clean for contrast.

**Streaming cursor:** Replace `|` pipe with a glowing quill-pen metaphor (CSS animation, no asset needed).

**Suggested actions:** Upgrade from plain secondary buttons to action cards — larger tap targets, subtle icon/illustration per action type (sword for attack, eye for perception, speech bubble for dialogue).

**Auto-save toast:** Flavour copy: "The chronicles are updated" instead of technical timestamp.

---

## Part 3: Wow Moments

These are the 6 emotional design moments, implemented after the foundation is solid:

1. **Campaign Preview Voice** — hover a campaign card for 1.5s, DM whispers a 15-second lore teaser. Fade out on mouse leave.

2. **Name Recognition** — after character name field loses focus, DM voice responds with the name: "Thorin. A strong name." Requires a lightweight TTS call (not full realtime session).

3. **The Threshold Crossing** — character created → full-screen transition → world art fades in → DM narrates opening in voice while text streams. "Then let the tale of Thorin, Dwarf Fighter, begin."

4. **Combat Voice Shift** — when combat triggers, DM voice shifts (via `session.update` voice parameter) to short, urgent delivery. Battle map expands simultaneously.

5. **"Previously On..."** — returning player gets a voiced 30-second recap of their last session. Requires `is_returning` flag on the opening narrative API + backend recap generation from conversation history.

6. **Player Roleplay Respect** — the "✋ DM has something to say" floor management card. The AI knows when to be quiet. This is what separates a tool from a companion.

---

## Implementation Order

1. **UI Critical Fixes** — loading states, markdown, error colours, alert(), type fixes
2. **shadcn Migration** — component-by-component across all pages
3. **Visual Polish** — tone cards, DM message styling, suggested actions
4. **Voice Infrastructure** — Foundry model deployment, token endpoint, WebRTC hook
5. **Voice Integration** — mic button, DM speaking indicator, floor management
6. **Wow Moments** — campaign preview voice, name recognition, threshold crossing, combat shift, "previously on", roleplay respect

Each phase is independently shippable and testable. Voice is always progressive enhancement — the app works fully without it.

---

## Testing Strategy

**UI polish:** Vitest unit tests for new components + Playwright E2E for critical user flows (campaign selection → character creation → gameplay).

**Voice:** Manual testing with browser mic permissions. Mock WebRTC connections in unit tests. Integration test with actual Foundry endpoint for the token flow. Playwright can test that voice UI elements appear/disappear correctly (without actual audio).

**Accessibility:** Voice is never required. All voice content is also displayed as text. Mic button has clear ARIA labels. Focus management during floor state changes. `prefers-reduced-motion` respected for all new animations.

---

## Scope Boundaries

**In scope:** Everything described above.

**Out of scope (future):**
- Avatar/video output from Voice Live API
- Ambient music/SFX (Phase 2 after voice ships)
- Wake-word activation ("DM, I...")
- Full-duplex always-listening mode (may evolve from Hybrid Campfire)
- Voice command for dice rolls (use structured UI for now)
- Per-NPC HD voices via Voice Live API (start with pitch/tempo shifts on native voices)
