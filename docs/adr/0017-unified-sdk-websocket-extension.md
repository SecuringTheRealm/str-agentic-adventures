# Unified SDK with WebSocket Client Extension

* Status: accepted
* Date: 2025-10-12

## Context and Problem Statement

The frontend application uses an auto-generated OpenAPI TypeScript client for REST API calls, which provides excellent type safety and automatic synchronization with backend changes. However, the backend also exposes WebSocket endpoints (`/api/ws/*`) for real-time features like chat streaming, dice rolls, and game state updates. These WebSocket endpoints are not covered by OpenAPI specifications, leading to:

1. **Inconsistent Development Experience**: Developers use the generated REST client for HTTP calls but must manually construct WebSocket URLs and handle connections using a custom React hook (`useWebSocket`)
2. **Type Duplication**: WebSocket message formats are defined in the backend but must be manually mirrored in the frontend
3. **Manual Synchronization**: When backend WebSocket protocols change, developers must manually update frontend code with no compile-time validation
4. **Testing Gaps**: REST endpoints have comprehensive tests via the OpenAPI client, but WebSocket functionality lacks equivalent test coverage
5. **Maintenance Overhead**: Separate codebases for REST and WebSocket clients increase maintenance burden

The goal is to provide a unified SDK that gives developers a consistent interface for both REST and WebSocket interactions with the backend.

## Decision Drivers

* **Consistent Developer Experience**: Single interface for all backend interactions
* **Type Safety**: Strong TypeScript typing for all WebSocket message types
* **Maintainability**: Reduce duplication and manual synchronization effort
* **Testing**: Enable comprehensive testing of WebSocket functionality
* **OpenAPI Limitations**: OpenAPI 3.x does not support WebSocket definitions
* **Minimal Disruption**: Maintain backward compatibility with existing code
* **Shared Configuration**: REST and WebSocket clients should use same base URL configuration

## Considered Options

* **Option 1: Continue Manual WebSocket Handling**
    * Keep the current approach with `useWebSocket` hook and manual URL construction
    * Pros: 
      * No additional code changes required
      * Familiar to current developers
      * Simple and straightforward
    * Cons:
      * Continues existing maintenance problems
      * Type safety gaps remain
      * No compile-time validation of WebSocket messages
      * Inconsistent with REST API approach

* **Option 2: Use AsyncAPI for WebSocket Schema**
    * Adopt AsyncAPI specification to define WebSocket endpoints and generate client
    * Pros:
      * Standardized approach for async/event-driven APIs
      * Could generate client code similar to OpenAPI
      * Schema-driven development
    * Cons:
      * AsyncAPI tooling is less mature than OpenAPI
      * Limited TypeScript generator quality
      * Doesn't integrate well with existing OpenAPI REST client
      * Additional specification to maintain
      * Steeper learning curve for team

* **Option 3: Extend OpenAPI Client with Manual WebSocket Module**
    * Create a manually implemented WebSocket client module alongside the generated REST client
    * Export both from a unified SDK interface
    * Define TypeScript interfaces for all WebSocket message types
    * Pros:
      * Consistent with existing OpenAPI approach
      * Full control over WebSocket client implementation
      * Can share configuration with REST client
      * Strong TypeScript typing for all messages
      * No additional specification formats to learn
    * Cons:
      * WebSocket types must be manually maintained
      * Changes to backend WebSocket protocol require manual frontend updates
      * More code to write and maintain than Option 1

* **Option 4: GraphQL Subscriptions or gRPC**
    * Migrate to a different protocol that unifies REST and real-time
    * Pros:
      * Single unified protocol
      * Strong typing throughout
    * Cons:
      * Major architectural change
      * Would require rewriting significant backend code
      * Outside scope of current FastAPI architecture
      * Steep learning curve

## Decision Outcome

Chosen option: "Extend OpenAPI Client with Manual WebSocket Module"

Justification:
* **Pragmatic Approach**: Works within current OpenAPI + FastAPI architecture without major changes
* **Type Safety**: Provides full TypeScript typing for all WebSocket messages through manual interfaces
* **Unified Interface**: Developers import both REST and WebSocket clients from same module (`services/api`)
* **Shared Configuration**: WebSocket client uses same base URL logic as REST client
* **FastAPI Best Practices**: Uses `root_path` and `servers` configuration for proper OpenAPI schema generation
* **Testability**: Enables comprehensive unit testing of WebSocket functionality
* **Gradual Migration**: Can be adopted incrementally without breaking existing code
* **Proven Pattern**: Many FastAPI projects follow this pattern when WebSocket support is needed
* **Team Familiarity**: Builds on existing OpenAPI knowledge rather than introducing new tools

Implementation approach:
1. Configure FastAPI with `root_path="/api"` and `servers` field for OpenAPI
2. Create `websocketClient.ts` with TypeScript interfaces for all message types
3. Implement WebSocket connection management with reconnection logic
4. Export alongside REST client from `services/api.ts`
5. Create React hook (`useWebSocketSDK`) for component integration
6. Refactor components to use new SDK

### FastAPI Server Configuration

The backend now uses FastAPI's `root_path` to properly structure the OpenAPI schema:

```python
app = FastAPI(
    root_path="/api",  # All routes are relative to /api
    servers=[{"url": "/api", "description": "API base path"}]
)
```

This ensures:
- OpenAPI paths are relative (e.g., `/game/character` not `/api/game/character`)
- The `servers` field tells clients where the API is hosted
- Generated clients properly construct URLs: `baseURL + serverPath + relativePath`
- Both REST and WebSocket endpoints follow consistent `/api/*` structure

## Consequences

### Positive
* **Unified Developer Experience**: Single import for all backend communication
* **Strong Type Safety**: All WebSocket messages have TypeScript interfaces
* **Better Testing**: WebSocket functionality can be unit tested with mocks
* **Shared Configuration**: Base URL and authentication logic shared between REST and WebSocket
* **Gradual Adoption**: Can migrate components one at a time
* **Documentation**: All API types documented in one place
* **IDE Support**: Full autocomplete and type checking for WebSocket messages

### Negative
* **Manual Maintenance**: WebSocket message types must be manually updated when backend changes
* **No Code Generation**: Unlike REST client, WebSocket client is hand-written
* **Potential Drift**: Risk of frontend/backend WebSocket protocol mismatches
* **Additional Code**: More code to maintain compared to status quo
* **Testing Overhead**: Requires mock WebSocket for comprehensive testing

### Risks and Mitigations
* **Risk**: WebSocket protocol changes break frontend without compile-time detection
  * **Mitigation**: Document WebSocket message schemas in shared location; add integration tests; establish process for coordinating WebSocket changes
* **Risk**: Developers bypass SDK and use WebSocket directly
  * **Mitigation**: Update documentation to recommend SDK; deprecate old `useWebSocket` hook; code reviews enforce SDK usage
* **Risk**: Message type interfaces become outdated
  * **Mitigation**: Include WebSocket message type review in backend PR checklist; maintain reference documentation
* **Risk**: Reconnection logic doesn't handle all edge cases
  * **Mitigation**: Comprehensive testing of connection states; fallback to REST API when WebSocket fails

## Links

* Related ADRs:
  * [0011-openapi-client-generation.md](0011-openapi-client-generation.md) - Foundation for REST client approach
  * [0008-multiplayer-implementation.md](0008-multiplayer-implementation.md) - WebSocket usage for multiplayer
* References:
  * [FastAPI WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
  * [OpenAPI Limitations with WebSockets](https://github.com/OAI/OpenAPI-Specification/issues/55)
  * [AsyncAPI Specification](https://www.asyncapi.com/docs/reference/specification/latest)
* Implementation:
  * WebSocket client: `frontend/src/api-client/websocketClient.ts`
  * React hook: `frontend/src/hooks/useWebSocketSDK.ts`
  * Usage documentation: `docs/specs/OPENAPI_CLIENT.md`
