# Unified API Client SDK (REST + WebSocket)

This document describes the unified SDK that provides both REST API and WebSocket communication with the FastAPI backend.

## Overview

The frontend uses a unified SDK that combines:
1. **REST API Client** - Auto-generated TypeScript client from OpenAPI schema
2. **WebSocket Client** - Manually implemented client for real-time features

This unified approach provides a single, consistent interface for all backend interactions, whether via HTTP or WebSocket.

## 🔄 Developer Workflow

**IMPORTANT**: The OpenAPI client is **NOT committed to git**. It is generated dynamically at build time and test time.

### Generated Files are NOT in Git

The `frontend/src/api-client/` directory contains:
- ✅ **Generated files** (api.ts, base.ts, configuration.ts, etc.) - **NOT in git**, excluded via .gitignore
- ✅ **Manual extensions** (websocketClient.ts, __tests__/) - **IN git**, manually maintained

### When the Client is Generated

The OpenAPI client is automatically generated:
- 📦 **During local setup**: Run `npm run generate:api` after cloning the repo
- 🏗️ **During CI/CD builds**: Generated before building the frontend
- 🧪 **Before tests run**: Generated to ensure tests have latest API types
- 🔄 **After backend API changes**: Developers regenerate to get new types

### How to Generate the Client Locally

1. **Start the backend server:**
   ```bash
   cd backend && uv run python -m app.main
   ```

2. **Generate the frontend client:**
   ```bash
   cd frontend && npm run generate:api
   ```

3. **Verify the update:**
   ```bash
   cd frontend && npm run build
   ```

4. **Test the integration:**
   ```bash
   cd frontend && npm test
   ```

### First-Time Setup

After cloning the repository:
```bash
# Backend setup
cd backend
uv sync
uv run python -m app.main  # Start backend in one terminal

# Frontend setup (in another terminal)
cd frontend
npm ci
npm run generate:api  # Generate OpenAPI client
npm start  # Start frontend dev server
```

### Troubleshooting

If generation fails:
- Ensure the backend is running on `http://localhost:8000`
- Check that `/openapi.json` endpoint is accessible (visit in browser)
- Verify no TypeScript compilation errors in the backend
- Check backend console for errors

### CI/CD Integration

**GitHub Actions** automatically:
1. Starts the backend server
2. Generates the OpenAPI client
3. Builds the frontend
4. Runs all tests

The generated client is **never committed** - it's created fresh for each build.

## Repository Structure

### Generated vs. Manual Files

**Generated Files** (NOT in git):
- `frontend/src/api-client/api.ts` - Generated API classes
- `frontend/src/api-client/base.ts` - Generated base classes  
- `frontend/src/api-client/configuration.ts` - Generated configuration
- `frontend/src/api-client/common.ts` - Generated common types
- `frontend/src/api-client/index.ts` - Generated exports
- `frontend/src/api-client/docs/*` - Generated documentation

**Manual Files** (IN git):
- `frontend/src/api-client/websocketClient.ts` - WebSocket client implementation
- `frontend/src/api-client/__tests__/` - Tests for manual extensions
- `frontend/src/api-client/.gitignore` - Excludes generated files
- `frontend/src/hooks/useWebSocketSDK.ts` - React hook for WebSocket
- `frontend/src/services/api.ts` - Unified exports

### Why Generated Files Aren't Committed

1. **Prevents merge conflicts** - No conflicts in auto-generated code
2. **Reduces repo size** - ~9,000 lines of generated code excluded
3. **Ensures synchronization** - Always generated fresh from backend schema
4. **Follows best practices** - Generated code shouldn't be in version control
- `frontend/src/components/GameInterface.tsx` - Updated to use unified SDK
- Various component files - Updated for stricter TypeScript types

## How It Works

### REST API
1. **Backend provides OpenAPI schema** at `http://localhost:8000/openapi.json`
2. **FastAPI uses `root_path` and `servers` configuration** to define `/api` as the base path
3. **OpenAPI paths are relative** to the server base (e.g., `/game/character` instead of `/api/game/character`)
4. **Generate client** with `npm run generate:api` 
5. **Client uses configured base URL** (`http://localhost:8000/api`) + relative paths from OpenAPI
6. **Wrapper functions** in `api.ts` maintain compatibility with existing frontend code
7. **Type aliases** provide backward compatibility for renamed types

### WebSocket API
1. **WebSocket client** provides strongly-typed message interfaces
2. **Connection methods** (`connectToCampaign`, `connectToChat`, `connectToGlobal`)
3. **Shared configuration** with REST client for consistent base URL
4. **React hook** (`useWebSocketSDK`) provides component-friendly interface

## FastAPI Server Configuration

The backend uses FastAPI's `root_path` and `servers` configuration to properly structure the API:

```python
app = FastAPI(
    title="AI Dungeon Master API",
    description="Backend API for the AI Dungeon Master application",
    version="0.1.0",
    root_path="/api",  # All routes are relative to /api
    servers=[
        {
            "url": "/api",
            "description": "API base path"
        }
    ],
)

# Routes are registered without the /api prefix
app.include_router(game_routes.router, prefix="/game")  # Results in /api/game/*
app.include_router(websocket_routes.router)  # Results in /api/ws/*
```

This configuration ensures:
- **OpenAPI schema has relative paths**: `/game/character` instead of `/api/game/character`
- **Servers field indicates base path**: Generated clients know to use `/api` as the base
- **Actual runtime routes**: Still served at `/api/game/*` and `/api/ws/*`
- **Client URL construction**: `baseURL + serverPath + relativePath = http://localhost:8000 + /api + /game/character`

## Usage Examples

### Using the REST Client

```typescript
import { gameApi, createCharacter } from "./services/api";

// Direct API call
const character = await gameApi.createCharacterApiGameCharacterPost({
  name: "Aragorn",
  race: Race.Human,
  characterClass: CharacterClass.Fighter,
  // ...
});

// Using wrapper function
const character = await createCharacter({
  name: "Aragorn",
  race: Race.Human,
  characterClass: CharacterClass.Fighter,
  // ...
});
```

### Using the WebSocket Client

```typescript
import { wsClient, type WebSocketMessage } from "./services/api";

// Connect to campaign WebSocket
const connection = wsClient.connectToCampaign(campaignId, {
  onMessage: (message: WebSocketMessage) => {
    switch (message.type) {
      case "dice_result":
        console.log("Dice rolled:", message.result);
        break;
      case "game_update":
        console.log("Game state updated:", message.data);
        break;
    }
  },
  onConnect: () => console.log("Connected"),
  onDisconnect: () => console.log("Disconnected"),
});

// Send a message
connection.send({
  type: "dice_roll",
  notation: "1d20",
  player_name: "Aragorn",
});

// Disconnect when done
connection.disconnect();
```

### Using the React Hook

```typescript
import { useWebSocketSDK } from "./hooks/useWebSocketSDK";

const MyComponent = () => {
  const { isConnected, sendMessage } = useWebSocketSDK({
    connectionType: "chat",
    campaignId: campaign.id,
    onMessage: (message) => {
      // Handle incoming messages
    },
  });

  const handleSendChat = () => {
    sendMessage({
      type: "chat_input",
      message: "Hello, world!",
      character_id: character.id,
    });
  };

  return <div>{isConnected ? "Connected" : "Disconnected"}</div>;
};
```

## WebSocket Message Types

The SDK provides TypeScript interfaces for all WebSocket message types:

### Chat Messages
- `ChatStartMessage` - Chat processing started
- `ChatStreamMessage` - Streaming chat content
- `ChatCompleteMessage` - Chat response complete
- `ChatInputMessage` - Send chat input to backend
- `ChatErrorMessage` - Chat error occurred

### Game Updates
- `DiceRollMessage` - Request dice roll
- `DiceResultMessage` - Dice roll result
- `GameUpdateMessage` - Game state update
- `CharacterUpdateMessage` - Character data update

### Connection Control
- `PingMessage` / `PongMessage` - Keep-alive heartbeat
- `ErrorMessage` - WebSocket error

All message types are exported from `frontend/src/api-client/websocketClient.ts`.

## Type Mappings

The generated API uses different names for some types:

| Frontend (Legacy) | Generated API | 
|-------------------|---------------|
| `Character` | `CharacterSheet` |
| `CharacterCreateRequest` | `CreateCharacterRequest` |
| `CampaignCreateRequest` | `CreateCampaignRequest` |

## Data Structure Changes

### Enums Now Lowercase
- Race: `"Human"` → `"human"`
- CharacterClass: `"Fighter"` → `"fighter"`

### Inventory Structure
- Legacy: `InventoryItem` with `name`, `quantity`
- Generated: `InventorySlot` with `item_id`, `quantity`

## Regenerating the Client

⚠️ **This section is deprecated. See the enhanced [Developer Workflow](#-developer-workflow) section above.**

When the backend API changes:

1. Start the backend: `cd backend && python -m app.main`
2. Generate new client: `cd frontend && npm run generate:api`
3. Review any type changes and update wrapper functions if needed

## Benefits

### REST API
1. **Automatic synchronization** - Frontend types update when backend changes
2. **Type safety** - All API calls are strongly typed
3. **No duplication** - Single source of truth for API types
4. **Documentation** - Generated docs in `src/api-client/docs/`

### WebSocket API
1. **Type safety** - All message types are strongly typed
2. **Consistent interface** - Same patterns as REST client
3. **Automatic reconnection** - Built-in reconnection logic
4. **Shared configuration** - Uses same base URL as REST client

### Unified SDK
1. **Single import** - Both REST and WebSocket from `services/api`
2. **Consistent patterns** - Similar API for both communication methods
3. **Better maintainability** - All API code in one place
4. **Reduced duplication** - No manual URL construction or type definitions

## 🧪 API Compatibility Testing

To ensure the frontend client stays synchronized with the backend API, automated tests verify:

### Backend Tests (`backend/tests/`)
- `test_api_compatibility.py` - Validates frontend/backend model compatibility
- `test_frontend_backend_integration.py` - Tests endpoint integration
- `test_openapi_schema_validation.py` - Validates OpenAPI schema accessibility

### Frontend Tests
Run the test suite to verify client compatibility:
```bash
cd frontend && npm test
```

### Manual Verification
Test the OpenAPI schema is accessible:
```bash
curl http://localhost:8000/openapi.json
```

## Known Issues

1. **Inventory compatibility** - Frontend expects `InventoryItem` but backend provides `InventorySlot`
2. **Optional fields** - Generated types are stricter about nullable fields
3. **Test updates needed** - Some tests need updates for new data formats

## Future Improvements

1. Align backend and frontend inventory data structures
2. Add validation for required fields in components
3. Consider automating client generation in CI/CD pipeline