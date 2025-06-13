# Data Storage Strategy for Game State and Assets

* Status: superseded
* Date: 2025-06-10
* Superseded by: Updated decision below (2025-06-12)

## Context and Problem Statement

The AI Dungeon Master system needs to persist various types of data including game state, character information, campaign narratives, and generated visual assets. We need to determine the most appropriate storage strategy that balances performance, reliability, and ease of use.

## Decision Drivers

* Need to store and retrieve structured game data (character sheets, campaign info)
* Need to manage generated visual assets (maps, character portraits)
* Requirement for session persistence and game state management
* Need for quick access to game state during play
* Compatibility with Semantic Kernel's memory systems

## Considered Options

* Option 1: Relational Database (PostgreSQL) + Blob Storage
    * PostgreSQL for structured data and Azure Blob Storage for assets
    * Pros:
      * Strong ACID properties for game state
      * Robust query capabilities for complex data retrieval
      * Clear separation of structured data and binary assets
    * Cons:
      * Higher operational complexity
      * Potential impedance mismatch between object models and relational schema

* Option 2: Document Database (CosmosDB) + Blob Storage
    * CosmosDB for JSON documents and Azure Blob Storage for assets
    * Pros:
      * Schema flexibility for evolving game data
      * JSON-native storage aligns with LLM outputs
      * Global distribution capabilities for multi-region deployments
    * Cons:
      * More expensive at scale
      * Less mature query capabilities for complex relationships

* Option 3: Hybrid Approach with Semantic Memory
    * Use Semantic Kernel's memory systems with backing storage
    * Pros:
      * Tight integration with agent architecture
      * Optimized for AI workloads
      * Simplified development model
    * Cons:
      * Newer technology with less established patterns
      * May require custom solutions for some scenarios

## Decision Outcome

**Original Decision: "Hybrid Approach with Semantic Memory"**
*Note: This decision was superseded due to implementation practicalities*

Justification:
* Semantic Kernel's memory capabilities align well with our agent-based architecture
* The semantic indexing capabilities support natural language queries from agents
* Flexible backing storage options allow us to choose appropriate persistent stores
* Reduces development complexity by leveraging the same framework for agent and data management

## Consequences

### Positive
* Simplified integration between agents and data storage
* Memory systems designed for AI workloads and natural language
* Flexibility to use different backing stores as needed
* Consistency in development approach

### Negative
* Reliance on evolving Semantic Kernel memory APIs
* May need to supplement with traditional storage for some scenarios
* Limited community examples for complex scenarios

### Risks and Mitigations
* Risk: Semantic Memory capabilities may not meet all our requirements
  * Mitigation: Design with abstraction layer to allow alternative implementations
* Risk: Performance issues at scale
  * Mitigation: Early performance testing and monitoring
* Risk: Limited tooling for data management
  * Mitigation: Develop custom tools for data administration as needed

## Updated Decision (2025-06-12)

**Revised Status: accepted**

Upon implementation review, the actual storage strategy implemented differs from the original decision. The system uses SQLAlchemy with SQL databases instead of Semantic Memory, which better aligns with Python ecosystem best practices and provides more mature tooling for complex relational data.

**New Decision Outcome: SQLAlchemy ORM with SQL Database**

Justification:
* SQLAlchemy provides mature, battle-tested ORM capabilities for Python applications
* SQL databases offer strong ACID properties for game state consistency
* Better tooling ecosystem for database administration and migrations
* Clear separation between data persistence and Semantic Kernel's AI capabilities
* SQLite for development with easy migration path to PostgreSQL for production
* JSON columns in SQL provide schema flexibility where needed

**Updated Consequences:**

### Positive
* Mature and stable data persistence layer with extensive Python ecosystem support
* Strong consistency guarantees for critical game state data
* Excellent tooling for database management, migrations, and monitoring
* Clear abstraction between data layer and AI agent functionality
* Easy local development with SQLite and production scaling with PostgreSQL

### Negative
* Traditional object-relational mapping complexity
* Requires separate solutions for semantic/vector search capabilities
* Less direct integration with Semantic Kernel's memory features

### Risks and Mitigations
* Risk: Impedance mismatch between object models and relational schema
  * Mitigation: Use JSON columns for flexible data and structured tables for core entities
* Risk: Limited semantic search capabilities in SQL
  * Mitigation: Add vector database integration (e.g., pgvector) when semantic search is needed
* Risk: Database migration complexity as schema evolves
  * Mitigation: Use Alembic migrations for version-controlled schema changes

## Original Decision Record

The original decision record is maintained for historical reference and to track the evolution of the data storage strategy.
