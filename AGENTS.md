# AI Agent Instructions

This file provides coding instructions for AI agents working on the Secure the Realm - Agentic Adventures project.

## Primary Instructions

For comprehensive coding guidelines and project setup instructions, see:
**[.github/copilot-instructions.md](.github/copilot-instructions.md)**

## Additional Guidelines

For detailed, domain-specific coding standards, refer to the instruction files in `.github/instructions/`:

- **[General Coding Standards](.github/instructions/general-coding.instructions.md)** - Foundation rules for all code
- **[Python Standards](.github/instructions/python.instructions.md)** - Backend development with FastAPI and Semantic Kernel  
- **[TypeScript/React Standards](.github/instructions/typescript-react.instructions.md)** - Frontend development
- **[Testing Guidelines](.github/instructions/testing.instructions.md)** - Comprehensive testing standards
- **[Documentation Standards](.github/instructions/documentation.instructions.md)** - Documentation best practices
- **[Database Guidelines](.github/instructions/database.instructions.md)** - Database and migration management
- **[ADR Guidelines](.github/instructions/adr.instructions.md)** - Architecture Decision Record standards

## Project Documentation

For comprehensive project documentation, refer to the docs in `docs/`:

- **[Azure OpenAI Requirements](docs/AZURE_OPENAI_REQUIREMENTS.md)** - Which endpoints require Azure OpenAI, configuration guide, and testing implications
- **[Testing Strategy](docs/TESTING_STRATEGY.md)** - Testing best practices, patterns, coverage requirements, and troubleshooting

**Note for AI Agents**: When creating new documentation files in the `docs/` directory, add references to them in this section of `AGENTS.md` and in the corresponding section of `.github/copilot-instructions.md`. When removing documentation files, remove their references from both files.

## Project Overview

AI-powered tabletop RPG application with Python FastAPI backend using Semantic Kernel and TypeScript React frontend. The system uses 6 specialized AI agents to replace a human Dungeon Master while maintaining creativity and D&D 5e SRD compliance.

Follow the comprehensive instructions in `.github/copilot-instructions.md` for detailed setup, build, and development workflows.