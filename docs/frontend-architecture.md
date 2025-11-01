# Frontend Architecture

**Generated:** 2025-11-01
**Part:** frontend (React + TypeScript + Vite)
**Framework:** React 19.2.0
**Build Tool:** Vite 7.1.9
**Language:** TypeScript 5.9.3

## Overview

Single Page Application (SPA) built with React 19 and TypeScript, featuring generated API client integration, component-based architecture, and WebSocket real-time communication for a D&D game management interface.

---

## API Integration Architecture

### Generated API Client Pattern

The frontend uses **OpenAPI Generator** to automatically generate a TypeScript Axios client from the backend's OpenAPI schema.

**Location:** `src/api-client/` (auto-generated, not committed to repo)
**Generator:** `@openapitools/openapi-generator-cli`
**Command:** `npm run generate:api`
**Source:** `http://localhost:8000/openapi.json`

### Service Layer (`src/services/api.ts`)

Wraps the generated client with:
- **Environment-aware base URL** (`getApiBaseUrl()`)
- **Error handling** with axios interceptors
- **Retry logic** for production reliability (exponential backoff)
- **Type aliases** for compatibility with existing code
- **Wrapper functions** for common operations

```typescript
// Example service wrapper
export const createCharacter = async (characterData: CreateCharacterRequest) => {
  const normalizedData = {...characterData, race: characterData.race?.toLowerCase()};
  const response = await gameApi.createCharacterGameCharacterPost(normalizedData);
  return response.data;
};
```

### API Client Exports

```typescript
export const gameApi = new GameApi(configuration);  // Generated REST client
export const wsClient = websocketClient;            // WebSocket unified SDK
export const apiClient = axios.create({...});       // Legacy direct axios client
```

### WebSocket Integration

**Location:** `src/api-client/websocketClient.ts` (auto-generated)
**Hook:** `src/hooks/useWebSocketSDK.ts`
**Endpoints:**
- `/ws/chat/{campaign_id}` - Campaign-specific chat
- `/ws/{campaign_id}` - Campaign events
- `/ws/global` - Global broadcasts

**Message Types:** `chat_message`, `chat_input`, `dice_roll`, `game_update`, `character_update`

---

## State Management

### Architecture: **Component-Local State (React Hooks)**

No global state management library (Redux/MobX/Zustand). State managed via:
- `useState` for local component state
- Props drilling for parent-child communication
- Custom hooks for shared logic

### Primary State Container: `App.tsx`

**Top-level state:**
```typescript
const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
const [currentCharacter, setCurrentCharacter] = useState<Character | null>(null);
const [gameStarted, setGameStarted] = useState(false);
const [showCharacterSelection, setShowCharacterSelection] = useState(false);
```

**Flow:**
1. CampaignSelection → `handleCampaignCreated()` → sets campaign + shows character selection
2. CharacterSelection → `handleCharacterSelected()` → sets character + starts game
3. GameInterface receives both campaign and character as props

### State Patterns by Component Category

| Component Category | State Pattern |
|--------------------|---------------|
| **App.tsx** | Top-level routing state (campaign, character, game started) |
| **Form Components** (CampaignCreation, CharacterCreation) | Local form state + controlled inputs |
| **Gallery/Selection** | Local selection state + data fetched from API |
| **Game Interface** | Local game state (messages, dice rolls) + WebSocket state |
| **Display Components** | Props-only (stateless) |

### Custom Hooks

**`useWebSocketSDK.ts`** - WebSocket connection management
- Handles connection lifecycle
- Message type routing
- Auto-reconnection logic
- State synchronization with server

---

## Component Inventory

### Component Architecture Pattern

**Pattern:** Component-based with CSS Modules
**Structure:** `ComponentName.tsx` + `ComponentName.module.css` + `ComponentName.test.tsx`

### Component Catalog (14 components)

#### 1. **BattleMap**
- **Category:** Display / Visualization
- **Purpose:** Render AI-generated battle maps
- **State:** Local (image loading state)
- **API Calls:** `generateBattleMap()`

#### 2. **CampaignCreation**
- **Category:** Form / Creation
- **Purpose:** Create new campaign with settings
- **State:** Local form state (name, description, setting, tone, homebrew rules)
- **API Calls:** `createCampaign()`
- **Validation:** Form validation on submit

#### 3. **CampaignEditor**
- **Category:** Form / Edit
- **Purpose:** Edit existing campaign details
- **State:** Local form state + original campaign data
- **API Calls:** `updateCampaign()`

#### 4. **CampaignGallery**
- **Category:** Gallery / Browse
- **Purpose:** Browse and select campaign templates
- **State:** Local (template list, loading, selected template)
- **API Calls:** `getCampaignTemplates()`

#### 5. **CampaignSelection**
- **Category:** Selection / Router
- **Purpose:** Choose existing campaign or create new
- **State:** Local (campaign list, view mode, selected campaign)
- **API Calls:** `getCampaigns()`, `getCampaign()`, `deleteCampaign()`, `cloneCampaign()`
- **Children:** CampaignCreation, CampaignGallery, CampaignEditor

#### 6. **CharacterCreation**
- **Category:** Form / Creation
- **Purpose:** Create new D&D character sheet
- **State:** Complex local form state (name, race, class, abilities, skills)
- **API Calls:** `createCharacter()`
- **Validation:** D&D 5e rules enforcement

#### 7. **CharacterSelection**
- **Category:** Selection / Router
- **Purpose:** Choose character or create new for campaign
- **State:** Local (character list, selected character)
- **API Calls:** `getCharacter()`, character listing
- **Children:** CharacterCreation, PredefinedCharacters

#### 8. **CharacterSheet**
- **Category:** Display / Info
- **Purpose:** Display full character sheet with stats
- **State:** Props-only (receives character data)
- **Features:** Abilities, skills, equipment, spells, HP tracking

#### 9. **ChatBox**
- **Category:** Communication / Input
- **Purpose:** Real-time chat interface for game
- **State:** Local (message input, message history)
- **WebSocket:** Yes (`useWebSocketSDK`)
- **Events:** Send/receive chat messages

#### 10. **DiceRoller**
- **Category:** Interactive / Game Mechanic
- **Purpose:** Roll dice with D&D notation (1d20, 2d6+3, etc.)
- **State:** Local (dice notation, roll results, animation state)
- **API Calls:** `rollDice()`
- **WebSocket:** Broadcasts roll results

#### 11. **GameInterface**
- **Category:** Container / Main Game View
- **Purpose:** Primary game session interface
- **State:** Local (game messages, current action, combat state)
- **API Calls:** `sendPlayerInput()`, combat actions, spell casting
- **WebSocket:** Yes (game state updates)
- **Children:** CharacterSheet, ChatBox, DiceRoller, GameStateDisplay, ImageDisplay

#### 12. **GameStateDisplay**
- **Category:** Display / Status
- **Purpose:** Show current game state (turn order, conditions, etc.)
- **State:** Props + local UI state
- **Features:** Combat tracker, status effects, initiative order

#### 13. **ImageDisplay**
- **Category:** Display / Media
- **Purpose:** Display AI-generated images (scenes, characters, items)
- **State:** Local (image loading, fullscreen mode)
- **API Calls:** `generateImage()`

#### 14. **PredefinedCharacters**
- **Category:** Gallery / Quick Select
- **Purpose:** Select from pre-generated character templates
- **State:** Local (template list, selected template)
- **Features:** Quick-start character creation

---

## Component Hierarchy

```
App
├── CampaignSelection
│   ├── CampaignGallery
│   ├── CampaignCreation
│   └── CampaignEditor
│
├── CharacterSelection
│   ├── CharacterCreation
│   └── PredefinedCharacters
│
└── GameInterface (Main Game)
    ├── CharacterSheet
    ├── ChatBox
    ├── DiceRoller
    ├── GameStateDisplay
    ├── ImageDisplay
    └── BattleMap
```

---

## Data Flow Patterns

### Campaign & Character Selection Flow
```
User → CampaignSelection → [Create/Select] → API Call
                                           ↓
                          handleCampaignCreated(campaign)
                                           ↓
                          App.setCurrentCampaign(campaign)
                                           ↓
                          CharacterSelection → [Create/Select] → API Call
                                                               ↓
                                              handleCharacterSelected(character)
                                                               ↓
                                              App.setCurrentCharacter(character)
                                                               ↓
                                              GameInterface (with campaign + character props)
```

### WebSocket Data Flow
```
Backend WS Event → wsClient → useWebSocketSDK hook → GameInterface state update → Re-render affected components
```

### API Call Pattern
```
Component → Service Wrapper (api.ts) → Generated GameApi Client → Axios Request → Backend
                                                                                     ↓
Component ← Update State ← Process Response ← Axios Response ← Backend Response ←┘
```

---

## Testing Strategy

### Unit Testing
- **Framework:** Vitest + Testing Library
- **Pattern:** Component behavior testing (user interactions, state changes)
- **Location:** Co-located `*.test.tsx` files
- **Coverage:** Form validation, API error handling, state transitions

### E2E Testing
- **Framework:** Playwright
- **Location:** `frontend/e2e/`
- **Coverage:** Full user flows (campaign creation → character selection → gameplay)
- **Browsers:** Chromium, Firefox, WebKit

### Test Configuration
- **vitest.config.ts:** Single-threaded execution to prevent test interference
- **playwright.config.ts:** Cross-browser testing configuration

---

## Build & Development

### Development Server
```bash
npm run dev          # Starts Vite dev server on http://127.0.0.1:5173
```

### Production Build
```bash
npm run build        # TypeScript check + Vite build → frontend/build/
```

### Code Quality
```bash
npm run lint         # Biome linter
npm run format       # Biome formatter
```

### Testing
```bash
npm run test         # Vitest watch mode
npm run test:run     # Vitest single run
npm run test:e2e     # Playwright E2E tests
```

### API Client Generation
```bash
npm run generate:api # Generate TypeScript client from backend OpenAPI spec
```

**Prerequisites:** Backend must be running at `http://localhost:8000`

---

## Environment Configuration

### Environment Variables

**Development (.env.local):**
```bash
VITE_API_URL=http://localhost:8000  # Backend API base URL
```

**Production:**
- `VITE_API_URL` set during build (Azure Container Apps deployment)
- Uses relative URLs if not set (same-origin deployment)

### URL Resolution (`src/utils/urls.ts`)

```typescript
export const getApiBaseUrl = () => {
  // Check environment variable first
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Fallback to relative path in production
  return '/api';  // Assumes reverse proxy routing
};
```

---

## Styling Approach

### CSS Modules
- **Pattern:** Component-scoped styles with `.module.css` files
- **Benefits:** Automatic class name hashing prevents conflicts
- **Global Styles:** `App.css` and `index.css` for shared styles

### Design Tokens
- CSS variables in `:root` for theming
- Consistent spacing, colors, typography

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `react` + `react-dom` | UI framework |
| `axios` | HTTP client for generated API |
| `vite` | Build tool and dev server |
| `typescript` | Type safety |
| `vitest` | Unit testing |
| `@testing-library/react` | Component testing utilities |
| `@playwright/test` | E2E testing |
| `@biomejs/biome` | Linting and formatting |
| `@openapitools/openapi-generator-cli` | API client generation |

---

## Performance Considerations

### Build Optimization
- **Code Splitting:** Vite automatic chunking
- **Tree Shaking:** Removes unused code
- **Minification:** Production builds minified

### Runtime Optimization
- **React 19 Features:** Automatic batching, concurrent rendering
- **Lazy Loading:** Components loaded on-demand (future enhancement)
- **WebSocket Efficiency:** Single connection per campaign

---

## Security Considerations

### XSS Prevention
- React's built-in XSS protection (escaping)
- Sanitization of user input before rendering

### API Security
- CORS handled by backend
- No authentication currently implemented (future: JWT tokens)

---

## Future Enhancements

### State Management
- Consider Context API for deeply nested prop drilling
- Or lightweight state library (Zustand) if complexity grows

### Performance
- Implement React.lazy() for code splitting
- Virtualized lists for large datasets (spell lists, item catalogs)
- Service Worker for offline support

### Features
- Real-time collaborative editing (multiple players)
- Character sheet auto-save with optimistic updates
- Undo/redo for game actions
