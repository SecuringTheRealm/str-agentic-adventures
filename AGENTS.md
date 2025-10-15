# AI Agent Instructions

This file provides coding instructions for AI agents working on the Secure the Realm - Agentic Adventures project.

## CRITICAL SECURITY RULES

**NEVER commit secrets, API keys, or credentials:**

1. **NO real values in `.env.example` files** - Only use placeholder values like `your-api-key-goes-here`
2. **NO real values in documentation** - All docs must use example/placeholder credentials
3. **NO real connection strings** - Always use `your-connection-string-here` format
4. **NO real endpoints with identifiable resource names** - Use `your-resource-name` as placeholder

**Before ANY commit involving configuration files:**
- Verify `.env.example` contains ONLY placeholder values
- Check documentation for accidentally pasted real credentials
- Confirm Azure resource names are genericized (not `stropenai`, but `your-resource-name`)

**Files that MUST NEVER contain real credentials:**
- `backend/.env.example`
- `frontend/.env.example`
- Any `*.md` documentation files
- Any committed configuration files

**Real credentials belong ONLY in:**
- Local `.env` files (gitignored)
- GitHub Secrets
- Azure Key Vault
- Environment variables on deployment platforms

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

# BMAD Agents
agents:
  - id: analyst
    path: .bmad-core/agents/analyst.md
  - id: architect
    path: .bmad-core/agents/architect.md
  - id: bmad-master
    path: .bmad-core/agents/bmad-master.md
  - id: bmad-orchestrator
    path: .bmad-core/agents/bmad-orchestrator.md
  - id: dev
    path: .bmad-core/agents/dev.md
  - id: pm
    path: .bmad-core/agents/pm.md
  - id: po
    path: .bmad-core/agents/po.md
  - id: qa
    path: .bmad-core/agents/qa.md
  - id: sm
    path: .bmad-core/agents/sm.md
  - id: ux-expert
    path: .bmad-core/agents/ux-expert.md