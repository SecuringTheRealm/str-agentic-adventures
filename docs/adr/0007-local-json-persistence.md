# Local JSON Persistence for Prototype Data

* Status: proposed
* Date: 2025-06-11

## Context and Problem Statement

During early development the project relies on in-memory data structures. This causes all state to be lost between runs. Persistent storage is not yet configured, but basic persistence is required for testing features like narrative memory and character management.

## Decision Drivers

* Need lightweight persistence without database setup
* Must support saving narrative memory and character data
* Should not introduce external dependencies
* Limited development time while prototyping

## Considered Options

* Option 1: JSON files stored on disk
    * Simple read/write of dictionaries to the filesystem
    * Pros: trivial to implement, no external services, works offline
    * Cons: not scalable, risk of file corruption

* Option 2: Lightweight SQLite database
    * Use an embedded relational database
    * Pros: stronger querying and concurrency control
    * Cons: additional dependency, more complex schema management

* Option 3: Cloud database service
    * Store data in PostgreSQL or CosmosDB as planned long term
    * Pros: production ready, scalable
    * Cons: requires infrastructure and credentials, overkill for prototype

## Decision Outcome

Chosen option: "JSON files stored on disk"

Justification:
* Quick to implement with Python's ``json`` module
* No external services required
* Keeps development environment simple

## Consequences

### Positive
* State persists across development runs
* Enables testing of memory features

### Negative
* Not safe for concurrent access
* Limited scalability

### Risks and Mitigations
* Risk: File corruption or accidental deletion
  * Mitigation: Regular backups during development

## Links

* Related ADRs: [ADR-0003](0003-data-storage-strategy.md)
* References: Python ``json`` module documentation
