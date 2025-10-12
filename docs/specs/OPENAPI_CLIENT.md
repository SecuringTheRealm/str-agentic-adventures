# Unified API Client SDK (REST + WebSocket)

This document describes the unified SDK that provides both REST API and WebSocket communication with the FastAPI backend.

## Overview

The frontend uses a unified SDK that combines:
1. **REST API Client** - Auto-generated TypeScript client from OpenAPI schema
2. **WebSocket Client** - Manually implemented client for real-time features

This unified approach provides a single, consistent interface for all backend interactions, whether via HTTP or WebSocket.

## 🔄 Developer Workflow

**IMPORTANT**: When the backend API changes, developers must regenerate the frontend client to maintain synchronization.

### When to Regenerate the Client

You must regenerate the client when:
- ✅ Adding new API endpoints
- ✅ Modifying existing endpoint parameters or responses
- ✅ Changing data models (request/response types)
- ✅ Updating enum values or field names
- ✅ After pulling backend changes from other developers

### How to Regenerate the Client

1. **Start the backend server:**
   ```bash
   cd backend && python -m app.main
   ```

2. **Regenerate the frontend client:**
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

### Troubleshooting

If the generation fails:
- Ensure the backend is running on `http://localhost:8000`
- Check that `/openapi.json` endpoint is accessible
- Verify no TypeScript compilation errors in the backend
- Review any API breaking changes that may require frontend updates

### Automated Validation

To validate the entire workflow automatically:
```bash
./scripts/validate-openapi-client.sh
```

This script checks:
- ✅ Backend server accessibility
- ✅ OpenAPI schema validity
- ✅ Client generation success
- ✅ TypeScript compilation

## Files Changed

### Generated REST Client
- `frontend/src/api-client/` - Complete generated client from OpenAPI schema
- `frontend/package.json` - Added `@openapitools/openapi-generator-cli` and npm script

### WebSocket Client SDK
- `frontend/src/api-client/websocketClient.ts` - Manually implemented WebSocket client
- `frontend/src/hooks/useWebSocketSDK.ts` - React hook for WebSocket connections
- `frontend/src/services/api.ts` - Unified export of both REST and WebSocket clients

### Updated Files
- `frontend/src/components/GameInterface.tsx` - Updated to use unified SDK
- Various component files - Updated for stricter TypeScript types

## How It Works

### REST API
1. **Backend provides OpenAPI schema** at `http://localhost:8000/openapi.json`
2. **Generate client** with `npm run generate:api` 
3. **Wrapper functions** in `api.ts` maintain compatibility with existing frontend code
4. **Type aliases** provide backward compatibility for renamed types

### WebSocket API
1. **WebSocket client** provides strongly-typed message interfaces
2. **Connection methods** (`connectToCampaign`, `connectToChat`, `connectToGlobal`)
3. **Shared configuration** with REST client for consistent base URL
4. **React hook** (`useWebSocketSDK`) provides component-friendly interface

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