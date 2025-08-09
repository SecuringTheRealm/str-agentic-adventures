---
applyTo: "**"
---

# Project general coding standards

## Repository Structure

- `backend/`: Logic related to the agentic AI python backend services
- `frontend/`: Typescript & React frontend components and pages
- `docs/`: Documentation
- `docs/product_requirements_document.md`: Product requirements document
- `docs/technical_specifications.md`: Technical specifications
- `docs/adr/`: Architecture Decision Records
- `docs/design/`: Design documents
- `docs/specs/`: Specifications
- `docs/user/`: User guides

## Required before each commit

- Run formatting and linting checks
- Ensure all tests pass (investigate and fix code issues, don't just rewrite tests)
- Clean up any legacy files (*.old, *.backup) and generated database files
- Update documentation as needed in proper `docs/` subdirectories
- Update the ADR files for any architectural decisions, if applicable - add new ADRs as needed, and update existing ones
- Add new ADRs to the ADR index
- Do not edit the ADR template

## General Guidelines

1. Maintain existing code structure and organization
2. Use consistent coding styles and patterns
3. Make minimal changes to achieve the goal - avoid unnecessary modifications
4. Remove legacy and orphaned files rather than leaving them as placeholders
5. Prevent binary files and database files from being committed to version control

## Writing and labelling guidelines

- Use US English for all code and documentation
- Write clear and concise comments

## Naming Conventions

### TypeScript/React

- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with underscore (\_)
- Use ALL_CAPS for constants

### Python

- Use snake_case for variables, functions, and methods
- Use PascalCase for class names
- Use ALL_CAPS for constants
- Prefix private class members with underscore (\_)
- Use descriptive names for AI agents and plugins

## Security and Configuration

### Environment Management

- Store sensitive data in environment variables.
- Never commit secrets or API keys.
- Use Azure Key Vault for production secrets.
- Secure all API endpoints with authentication.

## Error Handling

### General Principles

- Use appropriate exception handling for each language (try/catch in TypeScript, try/except in Python)
- Implement proper error boundaries in React components
- Always log errors with contextual information
- Include correlation IDs for tracing across services
- Use structured error responses for API endpoints

### AI-Specific Error Handling

- Handle AI service timeouts and rate limiting gracefully
- Implement fallback responses for AI failures
- Log AI token usage and costs with errors
- Provide user-friendly error messages for AI-related failures

## Answering Questions

- Answer all questions in the style of a friendly colleague, using informal language.
- Answer all questions in less than 1000 characters, and words of no more than 12 characters.

## File and Code Management

### Legacy File Cleanup

- **Remove orphaned legacy files** - Do not leave old files as placeholders (e.g., *.old, *.backup)
- Clean up legacy files once new implementation is in place (they remain in git history if needed)
- Check for and remove any generated binaries, caches, or database files before committing

### Binary and Database File Prevention

- **Never commit binary files** or database files (*.db, *.sqlite, SQLite files) to version control
- Use `.gitignore` to prevent accidental commits of generated files
- Remove any generated database files during development and testing
- Focus on source code and configuration, not generated artifacts
