# Multiplayer Implementation for Real-Time Collaborative Gameplay

* Status: superseded
* Date: 2025-01-27
* Superseded by: Updated decision below (2025-06-12)

## Context and Problem Statement

The AI Dungeon Master system currently supports single-player experiences but lacks the ability for multiple players to participate in the same campaign session simultaneously. Traditional tabletop RPGs are fundamentally collaborative experiences where multiple players interact with each other and the game world in real-time. We need to implement multiplayer functionality that enables real-time collaboration while maintaining the integrity of the AI-driven game experience and ensuring state consistency across all connected clients.

## Decision Drivers

* Need for real-time communication between multiple players in the same session
* Requirement to maintain game state synchronization across all connected clients
* Support for turn-based mechanics and initiative order in multiplayer context
* Integration with existing Semantic Kernel multi-agent architecture
* Compatibility with current SQLAlchemy data persistence layer
* Need for player authentication and session access control
* Scalability requirements for multiple concurrent campaigns
* Low-latency requirements for responsive collaborative gameplay

## Considered Options

* Option 1: WebSocket-based Real-Time Architecture with SignalR
    * Real-time bidirectional communication using Azure SignalR Service
    * Pros:
      * Native Azure integration with existing infrastructure
      * Excellent scalability and connection management
      * Built-in support for groups and user targeting
      * Automatic fallback to long polling for older browsers
      * Strong TypeScript support for frontend integration
    * Cons:
      * Additional Azure service dependency and cost
      * Learning curve for SignalR-specific patterns
      * Potential complexity in managing connection state

* Option 2: Server-Sent Events (SSE) with REST API
    * One-way real-time updates from server with REST for client actions
    * Pros:
      * Simpler implementation with existing HTTP infrastructure
      * No additional service dependencies
      * Built-in browser support for SSE
      * Easy to implement with FastAPI
    * Cons:
      * One-way communication requires separate API calls for player actions
      * Less efficient for high-frequency interactions
      * Limited browser connection pool (6 connections per domain)
      * No built-in group management for targeting specific players

* Option 3: Custom WebSocket Implementation
    * Direct WebSocket implementation with custom message handling
    * Pros:
      * Complete control over protocol and message format
      * No additional service dependencies
      * Lightweight implementation
    * Cons:
      * Significant development overhead for connection management
      * Need to implement scaling, reconnection, and group management
      * No built-in authentication or authorization features
      * Increased maintenance burden

## Decision Outcome

**Original Decision: "WebSocket-based Real-Time Architecture with SignalR"**
*Note: This decision was superseded due to Python ecosystem limitations*

Justification:
* SignalR provides enterprise-grade real-time communication with built-in scaling capabilities
* Native Azure integration aligns with existing infrastructure decisions (ADR 0005)
* Supports both real-time updates and direct player-to-player communication
* Built-in group management enables efficient session-based communication
* Strong TypeScript support integrates well with React frontend (ADR 0004)
* Automatic connection management and fallback options ensure reliability

## Updated Decision (2025-06-12)

**Revised Status: accepted**

Upon implementation review, it was discovered that Azure SignalR Service lacks robust Python SDK support, making it incompatible with our Python/FastAPI backend architecture (ADR 0001, 0005). The original decision has been updated to reflect technical reality.

**New Decision Outcome: Custom WebSocket Implementation with FastAPI**

Justification:
* Azure SignalR Service is primarily designed for .NET applications with limited Python support
* FastAPI provides excellent native WebSocket support with built-in connection management
* Custom implementation allows full control over message protocols and game-specific optimizations
* No additional Azure service costs or external dependencies
* Better alignment with Python ecosystem and existing FastAPI backend

**Updated Consequences:**

### Positive
* Native Python integration with FastAPI WebSocket support
* Complete control over connection management and message protocols
* No additional Azure service costs
* Simplified deployment and maintenance
* Game-specific optimizations possible

### Negative
* Manual implementation of connection pooling and group management
* Need to implement reconnection logic and connection state management
* Scaling considerations require manual load balancing solutions
* No built-in enterprise features like automatic fallbacks

### Risks and Mitigations
* Risk: Connection management complexity
  * Mitigation: Leverage FastAPI's built-in WebSocket support and proven patterns
* Risk: Scaling limitations with single-server WebSocket connections
  * Mitigation: Implement Redis pub/sub for multi-server WebSocket scaling when needed
* Risk: Manual reconnection handling
  * Mitigation: Implement robust client-side reconnection with exponential backoff

## Consequences

### Positive
* Real-time collaborative gameplay with instant updates for all players
* Scalable architecture that can support multiple concurrent campaigns
* Seamless integration with existing Azure OpenAI and Semantic Kernel infrastructure
* Enhanced social experience matching traditional tabletop RPG expectations
* Built-in reliability features reduce development overhead

### Negative
* Increased complexity in frontend state management for real-time updates
* Need to implement conflict resolution for simultaneous player actions
* Additional testing complexity for real-time scenarios

### Risks and Mitigations
* Risk: Network latency affecting gameplay experience
  * Mitigation: Implement optimistic UI updates and rollback mechanisms
* Risk: Session state conflicts when multiple players act simultaneously
  * Mitigation: Implement server-side action queuing and validation with turn-based locks
* Risk: WebSocket connection drops during critical gameplay moments
  * Mitigation: Implement automatic reconnection with state resynchronization
* Risk: Scaling limitations with single-server WebSocket connections
  * Mitigation: Implement Redis pub/sub for multi-server WebSocket scaling when needed

## Implementation Details

### Real-Time Communication Flow
1. Players join campaign sessions via authenticated WebSocket connections
2. Campaign-specific connection groups manage message routing to participants
3. Player actions trigger WebSocket broadcasts to campaign group members
4. AI agent responses distributed in real-time to all campaign participants

### State Synchronization Strategy
* Authoritative server maintains canonical game state in SQLAlchemy database
* Real-time state deltas broadcast via WebSocket for UI updates
* Client-side optimistic updates with server reconciliation
* Turn-based action queuing prevents state conflicts

### Integration Points
* **Multi-Agent Architecture** (ADR 0002): AI agents respond to aggregated player inputs
* **Data Storage** (ADR 0003): Session state persisted with multiplayer participant tracking
* **Frontend Architecture** (ADR 0004): React components subscribe to WebSocket events for real-time updates
* **Azure Integration** (ADR 0005): WebSocket infrastructure deployed with existing Azure Container Apps

## Links

* Related ADRs: [ADR 0002](0002-specialized-multi-agent-architecture.md), [ADR 0003](0003-data-storage-strategy.md), [ADR 0004](0004-react-typescript-frontend.md), [ADR 0005](0005-azure-openai-integration.md)
* References: [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/), [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)