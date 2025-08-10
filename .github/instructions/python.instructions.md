---
applyTo: "**/*.py"
---

# Python Project Coding Standards

All code must follow the [general coding guidelines](./general-coding.instructions.md).

## Dependency Management

- Use [UV](https://github.com/astral-sh/uv) for package and dependency management.
- Pin major versions, allow minor updates (e.g., `semantic-kernel>=1.0,<2.0`).
- Include Azure SDK packages for OpenAI integration.

## Linting and Formatting

- Use Ruff for linting and formatting.
- Configure Ruff to support async/await patterns.
- Apply type hints to all function signatures.
- Ensure all linting and formatting checks pass before submission.

## Coding Patterns

### Async/Await

- Use `async`/`await` for all AI-related operations.
- Wrap critical code in `try`/`except` blocks.
- Use `asyncio.gather()` for parallelism.
- Avoid blocking I/O in async functions.

### Error Handling

- Define custom exceptions for domain-specific cases.
- Use structured logging with contextual data.
- Apply circuit breaker patterns for external API calls.
- Add retry logic with exponential backoff for transient errors.

### Agent Communication

- Use Semantic Kernel's native messaging patterns.
- Ensure proper (de)serialization of agent data.
- Include correlation IDs in all agent requests/responses.
- Use event-driven patterns to decouple agents.

### Data Handling

- Use Pydantic models for data validation.
- Ensure proper serialization for campaign persistence.
- **MANDATORY: Use SQLAlchemy ORM for all database interactions** - Never use raw database connectors
- **FORBIDDEN: Direct use of sqlite3, psycopg2, or other database drivers** - Always use ORM sessions
- **Use dependency injection**: Access database via `get_session()` dependency
- **Model changes require migrations**: Update `app/models/db_models.py` + create Alembic migration
- Provide migration scripts for schema changes.

### Database Access Patterns

- **Correct**: `with next(get_session()) as db: db.query(Model).filter(...)`
- **Correct**: Use SQLAlchemy Session methods: `query()`, `add()`, `commit()`, `rollback()`
- **FORBIDDEN**: `import sqlite3; conn = sqlite3.connect(...)`
- **FORBIDDEN**: `import psycopg2; conn = psycopg2.connect(...)`
- **FORBIDDEN**: Raw SQL strings without SQLAlchemy text() wrapper
- **Required**: All model changes must include corresponding Alembic migrations

## Testing

### Test Structure

- Unit tests for agents and plugins.
- Integration tests for inter-agent workflows.
- End-to-end tests for full pipelines.
- Mock all external systems (Azure OpenAI, DBs, etc.).
- **NEVER rewrite tests just to make them pass** - investigate and fix code issues first.

### AI Testing Patterns

- Use deterministic outputs for reproducibility.
- Include failure scenarios and edge cases.
- Validate prompt outputs.
- Benchmark agent response latency.
- Test with mocked AI responses for consistency.

## Security and Configuration

### API Security

- Validate all inputs using Pydantic.
- Apply rate limiting to AI endpoints.
- Log requests for auditing.
- Enforce HTTPS on all external traffic.

## Documentation

### Code Documentation

- Add docstrings to all public functions/methods.
- Include usage examples for non-trivial agents.
- Document all configuration options.
- Maintain ADRs for major architectural changes.

### Agent Documentation

- Describe agent roles and capabilities.
- Provide prompt engineering guidance.
- Document inter-agent communication.
- Include troubleshooting steps for known issues.
