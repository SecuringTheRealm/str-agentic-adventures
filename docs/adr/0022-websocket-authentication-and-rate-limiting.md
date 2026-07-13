# WebSocket Authentication and Rate Limiting

* Status: accepted
* Date: 2026-03-28

## Context and Problem Statement

WebSocket endpoints in the application had no authentication or authorisation checks. Any client could connect to any campaign's WebSocket and broadcast messages to all connected clients. This created two serious issues:

1. **Unauthorised access:** Clients could join campaigns they did not own or participate in, receiving real-time game updates and sending actions on behalf of other players.
2. **Denial of service:** A malicious client could flood the WebSocket with messages, overwhelming the server and degrading the experience for legitimate players.

Additionally, the `PromptShieldMiddleware` and `SecurityHeadersMiddleware` (both subclasses of Starlette's `BaseHTTPMiddleware`) were blocking WebSocket upgrade requests entirely, because `BaseHTTPMiddleware` does not support the WebSocket scope. This meant WebSocket connections failed silently in production when these middleware were active.

## Decision Drivers

* WebSocket endpoints must validate that the target campaign exists in the database before accepting a connection
* Broadcast messages (`game_update` type) must not be accepted on the global WebSocket endpoint — only campaign-scoped endpoints
* Per-client rate limiting is needed to prevent message flooding
* Middleware must not break WebSocket connections

## Considered Options

* Option 1: Campaign validation + per-client rate limiting + middleware fix
    * Validate campaign existence on WebSocket connect; reject `game_update` on global WS; add sliding-window rate limiter; skip `BaseHTTPMiddleware` for WS scope
    * Pros: Minimal changes, addresses all identified vectors, no external dependencies
    * Cons: Rate limiting is in-memory (not shared across instances)

* Option 2: Full token-based WebSocket authentication
    * Issue signed tokens at session start, validate on every WS message
    * Pros: Stronger identity guarantee, works across instances
    * Cons: Requires token infrastructure, session management changes, significantly more complexity for current single-instance deployment

* Option 3: Reverse proxy rate limiting only
    * Rely on Azure Container Apps or a reverse proxy for rate limiting
    * Pros: No application code changes
    * Cons: Does not address campaign validation or broadcast injection; platform-dependent

## Decision Outcome

Chosen option: "Campaign validation + per-client rate limiting + middleware fix"

Justification:
* Addresses broadcast injection and message flooding with minimal code changes. Campaign-existence validation narrows, but does not close, unauthorised campaign access: `_campaign_exists()` only checks that the campaign row exists, not who the connecting client is — any client that knows a campaign UUID can connect, self-report an arbitrary `player_name`, and receive/send campaign traffic. Real per-connection identity verification is deferred to #511.
* In-memory rate limiting is sufficient for the current single-instance deployment model, and was extended in a later change to cover the chat and campaign WebSocket endpoints, not just the global one
* Middleware fix is a targeted change (check `scope["type"]` before processing) rather than an architectural overhaul
* Token-based authentication can be layered on later when multiplayer with user accounts is implemented (#511)

## Consequences

### Positive
* WebSocket connections to non-existent campaigns are rejected at connect time with a clear error
* Global WebSocket endpoint no longer accepts `game_update` broadcasts, preventing cross-campaign message injection
* Per-client rate limiting (30 messages per 60-second sliding window) prevents message flooding
* `PromptShieldMiddleware` and `SecurityHeadersMiddleware` no longer block WebSocket connections

### Negative
* Rate limiting is in-memory and per-instance — will not aggregate across multiple replicas if the application scales horizontally
* No per-user identity verification yet (deferred to multiplayer implementation)

### Risks and Mitigations
* Risk: In-memory rate limiter state is lost on restart
  * Mitigation: Acceptable for current deployment; can migrate to Redis-backed limiter when horizontal scaling is needed
* Risk: Campaign validation adds a database query on every WS connect
  * Mitigation: Query is lightweight (single row lookup by primary key); connection establishment is infrequent relative to message traffic

## Links

* Related ADRs: [ADR-0018 - Adopt Azure AI Agents SDK](0018-azure-ai-agents-sdk-adoption.md)
* References:
  * [Starlette WebSocket documentation](https://www.starlette.io/websockets/)
  * PR #730 — WebSocket authentication, rate limiting, and save slot constraint
