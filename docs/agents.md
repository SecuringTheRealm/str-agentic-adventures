# AI Agent Guidelines and Best Practices

This document serves as an overview and index of coding guidelines for AI agents contributing to the Secure the Realm - Agentic Adventures project. For detailed guidelines, refer to the specific instruction files in `.github/instructions/`.

## Quick Reference Guide

### Essential Guidelines for AI Contributions

- **Always follow testing discipline** - Don't rewrite tests to make them pass; fix the underlying code issues
- **Clean up after yourself** - Remove legacy files and avoid committing database files
- **Use proper documentation paths** - Create docs in `docs/` subdirectories, not in the repository root
- **Check for existing documentation** before creating new files to avoid duplication
- **Follow established naming conventions** for consistency across the project

## Detailed Instruction Files

### Core Development Guidelines

- **[General Coding Standards](./instructions/general-coding.instructions.md)** - Foundation rules for all code
  - Repository structure and organization
  - Naming conventions for TypeScript/React and Python
  - Security and configuration management
  - Error handling patterns

### Language-Specific Guidelines

- **[Python Standards](./instructions/python.instructions.md)** - Backend development with FastAPI and Semantic Kernel
  - Dependency management with UV
  - Async/await patterns for AI operations
  - Agent communication and data handling
  - Testing patterns for AI systems

- **[TypeScript/React Standards](./instructions/typescript-react.instructions.md)** - Frontend development
  - React component patterns and hooks
  - Test coverage requirements and tools
  - UI theming and responsive design
  - Linting and formatting with Biome

### Specialized Guidelines

- **[Testing Guidelines](./instructions/testing.instructions.md)** - Comprehensive testing standards
  - Test integrity and regression prevention
  - Testing tools and structure (Pytest, Vitest, Playwright)
  - AI-specific testing patterns
  - Coverage discipline and CI/CD integration

- **[Documentation Standards](./instructions/documentation.instructions.md)** - Documentation best practices
  - Proper documentation paths and organization
  - Markdown standards and formatting
  - ADR-specific requirements
  - Content maintenance and version control

- **[Database Guidelines](./instructions/database.instructions.md)** - Database and migration management
  - File cleanup and version control rules
  - Migration best practices
  - Security and performance considerations
  - Environment-specific configurations

- **[ADR Guidelines](./instructions/adr.instructions.md)** - Architecture Decision Record standards
  - ADR lifecycle management
  - Content requirements and validation
  - File naming and linking conventions
  - Immutability and superseding procedures

## Project-Specific Context

### Multi-Agent AI System

This project implements 6 specialized AI agents for tabletop RPG gameplay:
- **Dungeon Master Agent** - Orchestrates overall game flow
- **Narrator Agent** - Provides atmospheric descriptions
- **Scribe Agent** - Manages campaign data and character sheets
- **Combat MC Agent** - Handles combat encounters
- **Cartographer Agent** - Creates and manages maps
- **Artist Agent** - Generates visual content

### Technology Stack

- **Backend**: Python 3.12+ with FastAPI, Semantic Kernel, UV package manager
- **Frontend**: TypeScript + React with Material-UI
- **Testing**: Pytest (backend), Vitest + Playwright (frontend)
- **AI Integration**: Azure OpenAI Services
- **Database**: SQLAlchemy with PostgreSQL/SQLite

## Common Workflows

### Starting Development

```bash
# Backend setup
make deps && make run

# Frontend setup (in new terminal)
cd frontend && npm ci --legacy-peer-deps
npm run generate:api && npm start
```

### Before Committing

```bash
# Format and lint
make format && make lint

# Test
make test
cd frontend && npm run test:run

# Validate full build
cd frontend && npm run build
```

### After API Changes

```bash
# Regenerate OpenAPI client
cd frontend && npm run generate:api
```

## Key Principles for AI Agents

### Code Quality and Maintenance

1. **Minimal Changes** - Make the smallest possible changes to achieve the goal
2. **Test-Driven Fixes** - When tests fail, investigate and fix code before changing tests
3. **Clean File Management** - Remove legacy files (*.old) and prevent database file commits
4. **Documentation Discipline** - Use proper paths and avoid duplication

### AI-Specific Considerations

1. **Deterministic Testing** - Use mocks and fixtures for reproducible AI tests
2. **Error Handling** - Implement graceful fallbacks for AI service failures
3. **Performance Monitoring** - Track AI token usage and response times
4. **Security** - Never commit API keys or sensitive configuration

### Collaboration Guidelines

1. **Follow Existing Patterns** - Maintain consistency with established code structure
2. **Document Decisions** - Use ADRs for architectural changes
3. **Validate Changes** - Test complete user workflows after modifications
4. **Communicate Intent** - Use clear commit messages and PR descriptions

## Getting Help

- Review relevant instruction files before making changes
- Check existing ADRs for architectural context
- Test changes thoroughly using the validation workflows
- Follow the established patterns in the codebase

For questions about specific domains (testing, documentation, database, etc.), refer to the corresponding instruction file for detailed guidance.