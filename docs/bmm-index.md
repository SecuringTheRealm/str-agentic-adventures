# Project Documentation Index

**Project:** Securing the Realm - Agentic Adventures
**Generated:** 2025-11-01
**Type:** Multi-part repository (Frontend + Backend)
**Primary Language:** TypeScript (Frontend), Python (Backend)

---

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Repository Type** | Multi-part with 2 components |
| **Frontend** | React 19 + TypeScript + Vite |
| **Backend** | Python 3.12 + FastAPI + Azure AI Agents SDK |
| **Database** | PostgreSQL (prod) / SQLite (dev) |
| **Deployment** | Azure Container Apps |
| **Architecture Pattern** | Layered Client-Server with Agent-Based AI |

---

## Getting Started

**New to this project?** Start here:

1. **[Project Overview](./project-overview.md)** - Executive summary, tech stack, key features
2. **[Architecture](./architecture.md)** - System design and architectural decisions
3. **[Build Guide](./user/BUILD.md)** - Set up local development environment
4. **[PRD](./prd.md)** - Product requirements and specifications

---

## Generated Documentation (BMM Scan - 2025-11-01)

These documents were automatically generated from comprehensive codebase analysis:

### Backend Documentation

- **[API Contracts - Backend](./api-contracts-backend.md)**
  - 45+ REST API endpoints (character, campaign, combat, spells, NPCs, etc.)
  - 3 WebSocket endpoints for real-time communication
  - Request/response schemas
  - Error handling patterns

- **[Data Models - Backend](./data-models-backend.md)**
  - 5 database tables (characters, campaigns, npcs, npc_interactions, spells)
  - SQLAlchemy ORM models
  - Database schema diagram
  - Migration strategy with Alembic
  - JSON column schemas

### Frontend Documentation

- **[Frontend Architecture](./frontend-architecture.md)**
  - 14 React components with detailed descriptions
  - API integration patterns (generated OpenAPI client)
  - State management architecture (React hooks)
  - Component hierarchy and data flow
  - WebSocket integration
  - Testing strategy (Vitest + Playwright)
  - Build and deployment configuration

---

## Architecture & Design

### Core Architecture

- **[Main Architecture Document](./architecture.md)** - High-level system design, agent framework, integration patterns

### Architecture Decision Records (ADRs)

The `adr/` directory contains 19 detailed ADRs documenting major technical decisions:

#### AI & Agent Framework
- **[ADR-0001](./adr/0001-semantic-kernel-multi-agent-framework.md)** - Semantic Kernel multi-agent framework (superseded)
- **[ADR-0002](./adr/0002-specialized-multi-agent-architecture.md)** - Specialized multi-agent architecture
- **[ADR-0018](./adr/0018-azure-ai-agents-sdk-adoption.md)** - **Azure AI Agents SDK adoption** (current framework)
- **[ADR-0005](./adr/0005-azure-openai-integration.md)** - Azure OpenAI integration

#### Frontend
- **[ADR-0004](./adr/0004-react-typescript-frontend.md)** - React + TypeScript frontend
- **[ADR-0011](./adr/0011-openapi-client-generation.md)** - OpenAPI client generation
- **[ADR-0016](./adr/0016-frontend-build-modernization.md)** - Frontend build modernization
- **[ADR-0017](./adr/0017-unified-sdk-websocket-extension.md)** - Unified SDK WebSocket extension

#### Backend & Data
- **[ADR-0003](./adr/0003-data-storage-strategy.md)** - Data storage strategy
- **[ADR-0012](./adr/0012-fastapi-lifespan-migration.md)** - FastAPI lifespan migration
- **[ADR-0019](./adr/0019-api-prefix-configuration.md)** - API prefix configuration

#### Game Mechanics
- **[ADR-0006](./adr/0006-dnd-5e-character-progression-system.md)** - D&D 5e character progression system
- **[ADR-0008](./adr/0008-multiplayer-implementation.md)** - Multiplayer implementation

#### DevOps & Infrastructure
- **[ADR-0007](./adr/0007-github-actions-cicd-pipeline.md)** - GitHub Actions CI/CD pipeline
- **[ADR-0009](./adr/0009-container-app-deployment-strategy.md)** - Container App deployment strategy
- **[ADR-0013](./adr/0013-ci-workflow-optimization.md)** - CI workflow optimization
- **[ADR-0015](./adr/0015-copilot-workflow-optimization-with-dependency-caching.md)** - Copilot workflow optimization

#### Platform & Tooling
- **[ADR-0010](./adr/0010-technology-review-implementation.md)** - Technology review implementation
- **[ADR-0014](./adr/0014-multi-platform-ai-instruction-architecture.md)** - Multi-platform AI instruction architecture

**[ADR Index](./adr/index.md)** - Complete chronological list with summaries

---

## Specifications

### Testing
- **[Testing Strategy](./specs/TESTING_STRATEGY.md)** - Coverage targets (90%/85%), tools (pytest, Vitest, Playwright), patterns
- **[E2E Test Summary](./specs/E2E_TEST_SUMMARY.md)** - Playwright E2E test documentation

### API & Integration
- **[OpenAPI Client](./specs/OPENAPI_CLIENT.md)** - API client generation workflow, validation script

### Tooling
- **[UV Migration](./specs/UV_MIGRATION.md)** - Python dependency management with UV

---

## Operational Guides

### Setup & Configuration
- **[Azure OpenAI Requirements](./AZURE_OPENAI_REQUIREMENTS.md)** - Azure resource setup, environment variables, fallback modes
- **[Build Guide](./user/BUILD.md)** - Local development setup, prerequisites, common issues

### Development Workflow
- **[API Client Generation](./specs/OPENAPI_CLIENT.md)** - How to regenerate TypeScript client after backend changes
- **[Database Migrations](./data-models-backend.md#migration-strategy)** - Alembic workflow for schema changes

---

## Coding Standards & Guidelines

Detailed, file-specific standards are in `.github/instructions/`:

- **[General Coding Standards](../.github/instructions/general-coding.instructions.md)** - Cross-language principles
- **[Python Standards](../.github/instructions/python.instructions.md)** - Backend code style, patterns, error handling
- **[TypeScript/React Standards](../.github/instructions/typescript-react.instructions.md)** - Frontend code style, component patterns
- **[Database Standards](../.github/instructions/database.instructions.md)** - SQLAlchemy patterns, migration workflows
- **[Testing Standards](../.github/instructions/testing.instructions.md)** - Test integrity, failure resolution, coverage
- **[Documentation Standards](../.github/instructions/documentation.instructions.md)** - File naming, content standards
- **[ADR Standards](../.github/instructions/adr.instructions.md)** - ADR creation and maintenance

**High-Level Repository Guidelines:** [AGENTS.md](../AGENTS.md)

---

## Reference Documentation

### Contributing
- **[Contributions](./contributions.md)** - Acknowledgements of critical dependencies and open-source projects

### Backend Reference
- **[Agent Framework Base](../backend/app/agent_framework_base.py)** - `AgentFrameworkManager` singleton for all agents
- **[Azure OpenAI Client](../backend/app/azure_openai_client.py)** - `azure_openai_client` singleton for chat completions
- **[Configuration](../backend/app/config.py)** - Pydantic settings with environment variable loading

### Frontend Reference
- **[API Service](../frontend/src/services/api.ts)** - API client wrappers, retry logic, type aliases
- **[Environment Utils](../frontend/src/utils/environment.ts)** - Runtime mode detection
- **[URL Utils](../frontend/src/utils/urls.ts)** - API base URL resolution

---

## Development Workflows

### Making Changes

#### Backend Changes
1. Edit code in `backend/app/`
2. Add/update tests in `backend/tests/`
3. Run `make test` and `make lint`
4. If schema changed: `alembic revision --autogenerate -m "description"`
5. If API changed: Regenerate frontend client (`cd frontend && npm run generate:api`)

#### Frontend Changes
1. Edit code in `frontend/src/`
2. Add/update tests (unit: `*.test.tsx`, E2E: `e2e/*.spec.ts`)
3. Run `npm run test:run` and `npm run lint`
4. If using new API endpoints: Ensure API client is up-to-date

### Common Tasks

| Task | Command |
|------|---------|
| Start backend | `make run` |
| Start frontend | `cd frontend && npm run dev` |
| Run backend tests | `make test` |
| Run frontend unit tests | `cd frontend && npm run test:run` |
| Run E2E tests | `cd frontend && npm run test:e2e` |
| Lint backend | `make lint` |
| Lint frontend | `cd frontend && npm run lint` |
| Generate API client | `cd frontend && npm run generate:api` |
| Create migration | `cd backend && alembic revision --autogenerate -m "msg"` |

---

## CI/CD Pipelines

**Location:** `.github/workflows/`

- **PR Workflow:** Lint, test, build validation (triggers on pull requests)
- **Deploy Workflow:** Build containers, deploy to Azure, smoke tests (triggers on main branch)

**Pre-commit Hooks:** None currently configured

---

## Project-Specific Tools

### BMAD Framework

The `bmad/` directory contains the BMad methodology framework for AI-assisted development workflows:

- **Agents:** Product Manager, Architect, Developer, QA, Scribe, etc.
- **Workflows:** PRD creation, architecture design, story generation, code review
- **Templates:** Documentation templates, workflow definitions

**Purpose:** Structured workflows for AI-driven software development planning and execution

**Note:** BMAD is a development tool, not part of the application runtime

---

## Browsing by Concern

### Want to understand...

**The overall system?**
→ Start with [Project Overview](./project-overview.md) and [Architecture](./architecture.md)

**How the frontend works?**
→ [Frontend Architecture](./frontend-architecture.md) for components, state, API integration

**How the backend works?**
→ [API Contracts](./api-contracts-backend.md) for endpoints, [Data Models](./data-models-backend.md) for database

**How AI agents work?**
→ [ADR-0018 (Azure AI Agents SDK)](./adr/0018-azure-ai-agents-sdk-adoption.md) + `backend/app/agents/` source code

**How to set up locally?**
→ [Build Guide](./user/BUILD.md) + [Azure OpenAI Requirements](./AZURE_OPENAI_REQUIREMENTS.md)

**How to contribute?**
→ [AGENTS.md](../AGENTS.md) for guidelines + `.github/instructions/` for detailed standards

**Why a technical decision was made?**
→ Browse [ADR Index](./adr/index.md) or search `docs/adr/*.md`

**How to test?**
→ [Testing Strategy](./specs/TESTING_STRATEGY.md) + `.github/instructions/testing.instructions.md`

**How data is stored?**
→ [Data Models](./data-models-backend.md) for schema + [ADR-0003](./adr/0003-data-storage-strategy.md) for rationale

---

## External Resources

- **GitHub Repository:** https://github.com/SecuringTheRealm/str-agentic-adventures
- **Azure OpenAI Documentation:** https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Azure AI Agents SDK:** https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents
- **D&D 5e SRD:** https://dnd.wizards.com/resources/systems-reference-document

---

## Document Maintenance

**Last Generated:** 2025-11-01
**Scan Type:** Exhaustive (all source files analyzed)
**Generator:** BMM document-project workflow v1.2.0

**Regenerating Documentation:**
- Run `/bmad:bmm:workflows:document-project` in Claude Code
- Choose "Re-scan entire project" option
- Select "Exhaustive Scan" for complete analysis

**Manual Updates:**
- Architecture decisions → Add ADRs to `docs/adr/`
- API changes → Regenerate [API Contracts](./api-contracts-backend.md)
- Database schema → Update [Data Models](./data-models-backend.md)
- Component changes → Update [Frontend Architecture](./frontend-architecture.md)

---

## License

This project is MIT licensed. See [LICENSE](../LICENSE) for details.

---

**Navigation Tips:**
- Use your IDE's file search to quickly locate documents
- ADRs are numbered chronologically (0001-0019)
- Component documentation includes file locations (e.g., `src/components/GameInterface.tsx`)
- Database table names match ORM class names (e.g., `Campaign` class → `campaigns` table)
