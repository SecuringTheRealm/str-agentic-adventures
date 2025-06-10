---
applyTo: "**/*.py"
---

# Project coding standards for Python

Apply the [general coding guidelines](./general-coding.instructions.md) to all code.

## Project Architecture

This project uses Microsoft Semantic Kernel with Azure OpenAI for a multi-agent AI system powering tabletop RPG experiences.

### Core Technologies
- **Microsoft Semantic Kernel**: Primary framework for agent orchestration
- **Azure OpenAI**: LLM integration for AI agents
- **Python 3.11+**: Backend runtime
- **FastAPI/Flask**: Web API framework (when implemented)
- **SQLAlchemy**: Database ORM for persistence
- **Pydantic**: Data validation and serialization

## Code Organization

### Directory Structure
```
backend/
├── agents/          # AI agent implementations
├── plugins/         # Semantic Kernel plugins
├── models/          # Data models and schemas
├── services/        # Business logic services
├── api/             # API endpoints
├── config/          # Configuration management
├── tests/           # Test suites
└── utils/           # Utility functions
```

### Agent Architecture
- Each AI agent should be a separate module in `agents/`
- Agents must inherit from base agent class
- Use dependency injection for agent communication
- Follow the orchestrator pattern with Dungeon Master as primary agent

## Dependency Management

- Use `requirements.txt` for production dependencies
- Use `requirements-dev.txt` for development dependencies
- Pin major versions but allow minor updates (e.g., `semantic-kernel>=1.0,<2.0`)
- Include Azure SDK packages for OpenAI integration

## Linting and Formatting

- Use Ruff for linting and formatting
- Configure Ruff for async/await patterns
- Use type hints for all function signatures
- Ensure all linting and formatting rules pass before submitting code

## Coding Patterns

### Async/Await
- Use async/await for all AI operations
- Implement proper error handling with try/except blocks
- Use asyncio.gather() for parallel agent operations
- Avoid blocking calls in async functions

### Error Handling
- Create custom exception classes for domain-specific errors
- Use structured logging with contextual information
- Implement circuit breaker patterns for external API calls
- Add retry logic with exponential backoff for transient failures

### Agent Communication
- Use Semantic Kernel's native messaging patterns
- Implement proper serialization for agent data exchange
- Add request/response correlation IDs for debugging
- Use events for loose coupling between agents

### Data Handling
- Use Pydantic models for all data validation
- Implement proper serialization for campaign persistence
- Use SQLAlchemy for database operations
- Add data migration scripts for schema changes

## Testing

### Test Structure
- Unit tests for individual agents and plugins
- Integration tests for agent interactions
- End-to-end tests for complete workflows
- Mock external dependencies (Azure OpenAI, databases)

### AI Testing Patterns
- Use deterministic responses for reproducible tests
- Test error scenarios and edge cases
- Validate prompt engineering outputs
- Include performance benchmarks for agent response times

## Security and Configuration

### Environment Management
- Use environment variables for sensitive configuration
- Never commit API keys or secrets to version control
- Use Azure Key Vault for production secrets
- Implement proper authentication for API endpoints

### API Security
- Validate all input data with Pydantic
- Implement rate limiting for AI operations
- Add request logging for audit trails
- Use HTTPS for all external communications

## Performance Optimization

### AI Operations
- Implement caching for repeated AI requests
- Use connection pooling for database operations
- Add monitoring for token usage and costs
- Implement request queuing for high-load scenarios

### Memory Management
- Monitor memory usage for long-running sessions
- Implement proper cleanup for completed games
- Use weak references where appropriate
- Add garbage collection hints for large objects

## Logging and Monitoring

### Structured Logging
- Use JSON format for log messages
- Include correlation IDs for request tracking
- Log agent decisions and reasoning paths
- Add performance metrics for AI operations

### Monitoring Requirements
- Track AI token usage and costs
- Monitor agent response times
- Log error rates and failure patterns
- Add health checks for external dependencies

## Documentation

### Code Documentation
- Document all public methods with docstrings
- Include usage examples for complex agents
- Document configuration parameters
- Add architectural decision records for major changes

### Agent Documentation
- Document agent responsibilities and capabilities
- Include prompt engineering guidelines
- Document inter-agent communication patterns
- Add troubleshooting guides for common issues
