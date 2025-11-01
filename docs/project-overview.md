# Project Overview: Securing the Realm - Agentic Adventures

**Generated:** 2025-11-01
**Project Type:** Multi-part Web Application
**Repository:** https://github.com/SecuringTheRealm/str-agentic-adventures

## Executive Summary

An AI-powered Dungeons & Dragons game management system leveraging Azure AI Agents SDK to create an intelligent, autonomous Dungeon Master experience. The application combines a React-based frontend with a FastAPI backend, utilizing Azure OpenAI for natural language generation, dynamic storytelling, and intelligent NPC interactions.

## Project Purpose

Create an immersive tabletop RPG experience where AI agents handle the Dungeon Master role, generate content dynamically, and manage complex game mechanics automatically—allowing players to focus on storytelling and character development.

## Repository Structure

```
str-agentic-adventures/
├── frontend/          # React 19 + TypeScript + Vite SPA
├── backend/           # Python 3.12 + FastAPI + Azure AI Agents SDK
├── docs/              # Architecture, ADRs, specs, and generated documentation
├── infra/             # Azure deployment configuration (Container Apps)
├── .github/           # CI/CD workflows + coding instructions
├── bmad/              # BMAD workflow automation framework
└── scripts/           # Utility scripts
```

**Repository Type:** Monorepo (multi-part)
**Architecture:** Client-server with clear separation of concerns

---

## Technology Stack Summary

### Frontend (React SPA)

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **UI Framework** | React | 19.2.0 | Component-based UI |
| **Language** | TypeScript | 5.9.3 | Type-safe development |
| **Build Tool** | Vite | 7.1.9 | Fast HMR + optimized builds |
| **HTTP Client** | Axios | 1.12.2 | Generated API client |
| **State** | React Hooks | Built-in | Local component state |
| **Testing** | Vitest + Playwright | 3.2.4 / 1.56.0 | Unit + E2E testing |
| **Code Quality** | Biome | 2.2.5 | Unified lint + format |

### Backend (API + Agent Framework)

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **API Framework** | FastAPI | ≥0.100.0 | High-performance async API |
| **Language** | Python | 3.12+ | Modern Python features |
| **AI Framework** | Azure AI Agents SDK | ≥1.0.0 | Intelligent agent orchestration |
| **AI Model** | Azure OpenAI | GPT-4 | Natural language generation |
| **Database** | PostgreSQL/SQLite | 2.0+ | Relational data storage |
| **ORM** | SQLAlchemy | ≥2.0.0 | Async database access |
| **Migrations** | Alembic | ≥1.11.0 | Schema versioning |
| **Server** | Uvicorn | ≥0.22.0 | ASGI server with WebSockets |
| **Testing** | pytest | ≥7.4.0 | Test framework |
| **Code Quality** | Ruff | ≥0.1.5 | Fast linting + formatting |

---

## Architecture Classification

**Pattern:** Layered Client-Server with Agent-Based AI
**Communication:** REST API + WebSocket for real-time events
**Data Flow:** Unidirectional (Frontend → API → Agents → Database)

### Frontend Architecture
- **Pattern:** Component-based SPA with generated API client
- **State Management:** Component-local (React hooks, no global state library)
- **Routing:** Conditional rendering based on game state

### Backend Architecture
- **Pattern:** Layered API with Agent Framework
- **Layers:**
  1. **API Layer** (`app/api/`) - REST endpoints, request validation
  2. **Service Layer** (`app/services/`) - Business logic, data orchestration
  3. **Agent Layer** (`app/agents/`) - AI-powered game masters (DM, Scribe, Artist, Combat Cartographer)
  4. **Data Layer** (`app/models/`, `app/database.py`) - ORM models, database access
- **Agents:**
  - **Dungeon Master Agent:** Narrative generation, world-building, decision adjudication
  - **Scribe Agent:** Character creation, progression, D&D 5e rules enforcement
  - **Artist Agent:** Image generation for scenes, characters, items
  - **Combat Cartographer:** Battle map generation

---

## Key Features

### 1. **Campaign Management**
- Create custom campaigns with settings, tone, and homebrew rules
- Clone template campaigns
- World generation via AI
- Campaign persistence and session tracking

### 2. **Character System**
- D&D 5e character creation with full rules support
- Character progression (leveling, ability score increases, new features)
- Equipment and inventory management
- Spell casting system with concentration tracking

### 3. **AI-Powered Game Master**
- Dynamic narrative generation based on player actions
- Intelligent NPC interactions with persistent memory
- Adaptive difficulty and content generation
- Fallback to deterministic logic when AI unavailable

### 4. **Combat System**
- Turn-based combat with initiative tracking
- Spell casting with save DCs, attack rolls, damage calculation
- Concentration checks and condition management
- Combat event logging

### 5. **Real-Time Multiplayer**
- WebSocket-based chat
- Shared game state updates
- Dice roll broadcasts
- Campaign-scoped and global event channels

### 6. **Content Generation**
- AI-generated images (scenes, characters, items) via Artist agent
- Battle map generation via Combat Cartographer
- NPC personality and stat block generation
- World lore and quest hooks

---

## Documentation Index

### Generated Documentation (from this scan)
- **[API Contracts - Backend](./api-contracts-backend.md)** - REST API and WebSocket endpoints
- **[Data Models - Backend](./data-models-backend.md)** - Database schema, ORM models, migrations
- **[Frontend Architecture](./frontend-architecture.md)** - React components, API integration, state management

### Existing Architecture Documentation
- **[Architecture Decision Records (ADRs)](./adr/)** - 19 ADRs covering major technical decisions
  - ADR-0001: Semantic Kernel multi-agent framework
  - ADR-0018: Azure AI Agents SDK adoption
  - ADR-0011: OpenAPI client generation
  - ADR-0004: React + TypeScript frontend
  - ADR-0005: Azure OpenAI integration
- **[Main Architecture Document](./architecture.md)** - High-level system architecture
- **[PRD](./prd.md)** - Product Requirements Document

### Specifications
- **[Testing Strategy](./specs/TESTING_STRATEGY.md)** - Test coverage, patterns, tools
- **[E2E Test Summary](./specs/E2E_TEST_SUMMARY.md)** - Playwright test documentation
- **[OpenAPI Client](./specs/OPENAPI_CLIENT.md)** - Client generation workflow
- **[UV Migration](./specs/UV_MIGRATION.md)** - Python dependency management

### Operational Documentation
- **[Azure OpenAI Requirements](./AZURE_OPENAI_REQUIREMENTS.md)** - Setup and configuration
- **[Build Guide](./user/BUILD.md)** - Local development setup

### Code Standards
- **[General Coding Standards](../.github/instructions/general-coding.instructions.md)**
- **[Python Standards](../.github/instructions/python.instructions.md)**
- **[TypeScript/React Standards](../.github/instructions/typescript-react.instructions.md)**
- **[Database Standards](../.github/instructions/database.instructions.md)**
- **[Testing Standards](../.github/instructions/testing.instructions.md)**
- **[Documentation Standards](../.github/instructions/documentation.instructions.md)**
- **[ADR Standards](../.github/instructions/adr.instructions.md)**

---

## Development Workflow

### Prerequisites
- **Python:** 3.12+ (via [UV](https://github.com/astral-sh/uv))
- **Node.js:** ≥22.0.0
- **Java:** OpenJDK (for OpenAPI generator)
- **Database:** SQLite (dev) or PostgreSQL (prod)

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/SecuringTheRealm/str-agentic-adventures.git
cd str-agentic-adventures

# 2. Backend setup
cd backend
cp .env.example .env  # Configure Azure OpenAI credentials
cd ..
make deps              # Install Python dependencies via UV

# 3. Frontend setup
cd frontend
npm install
cp .env.example .env.local  # Configure VITE_API_URL if needed
```

### Generate API Client (Required first-time setup)

```bash
# Start backend first
make run  # Backend runs on http://localhost:8000

# In separate terminal, generate frontend API client
cd frontend
npm run generate:api
```

### Development

```bash
# Terminal 1: Backend
make run              # http://localhost:8000

# Terminal 2: Frontend
cd frontend
npm run dev           # http://127.0.1.5173
```

### Testing

```bash
# Backend tests
make test

# Frontend tests
cd frontend
npm run test:run      # Unit tests (Vitest)
npm run test:e2e      # E2E tests (Playwright)
```

### Code Quality

```bash
# Backend
make lint
make format

# Frontend
cd frontend
npm run lint
npm run format
```

---

## Deployment

### Platform: **Azure Container Apps**

**Infrastructure:** `infra/` directory contains Azure deployment configuration
**CI/CD:** GitHub Actions workflows in `.github/workflows/`

### Deployment Workflow

1. **PR Workflow:** Lint, test, build validation
2. **Deploy Workflow:** Build containers, deploy to Azure, run E2E smoke tests
3. **Environment:** Single production environment with Azure-managed PostgreSQL

### Environment Variables

**Backend:**
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - API key for Azure OpenAI
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Model deployment name
- `AZURE_OPENAI_API_VERSION` - API version
- `DATABASE_URL` - PostgreSQL connection string

**Frontend:**
- `VITE_API_URL` - Backend API base URL (set during build)

---

## Integration Points

### Frontend → Backend
- **Protocol:** HTTP/HTTPS (REST API)
- **Format:** JSON
- **Client:** Generated TypeScript Axios client from OpenAPI spec
- **Endpoints:** 45+ REST endpoints for game operations
- **WebSocket:** 3 WebSocket endpoints for real-time features

### Backend → Azure OpenAI
- **Protocol:** HTTPS
- **SDK:** Azure AI Agents SDK + Azure OpenAI SDK
- **Model:** GPT-4 (configurable deployment)
- **Features:** Chat completions, streaming responses, function calling

### Backend → Database
- **Protocol:** PostgreSQL wire protocol / SQLite file access
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic (auto-run on startup)
- **Tables:** 5 tables (characters, campaigns, npcs, npc_interactions, spells)

---

## Quick Reference

### Repository Statistics (Approximate)
- **Total Components:** 14 React components
- **API Endpoints:** 45+ REST endpoints, 3 WebSocket endpoints
- **Database Tables:** 5 tables
- **Agent Implementations:** 4 AI agents
- **ADRs:** 19 architecture decision records
- **Test Coverage Target:** 90% for new code, 85% overall

### Key Directories

| Path | Purpose |
|------|---------|
| `frontend/src/components/` | React UI components |
| `frontend/src/services/` | API client wrappers |
| `backend/app/api/` | FastAPI route definitions |
| `backend/app/agents/` | AI agent implementations |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/migrations/` | Alembic database migrations |
| `docs/adr/` | Architecture Decision Records |
| `.github/workflows/` | CI/CD pipelines |
| `.github/instructions/` | Detailed coding standards |

---

## Getting Help

- **Issues:** https://github.com/SecuringTheRealm/str-agentic-adventures/issues
- **Documentation:** This repository's `docs/` directory
- **Coding Standards:** `.github/instructions/` for detailed guidelines
- **API Docs:** http://localhost:8000/docs (when backend running)

---

## License

MIT License - See [LICENSE](../LICENSE) file

---

## Project Status

**Current Phase:** Active Development (Alpha)
**Latest Version:** 0.1.0
**Last Major Update:** 2025-11-01

**Recent Milestones:**
- ✅ Azure AI Agents SDK integration (ADR-0018)
- ✅ OpenAPI client generation (ADR-0011)
- ✅ Frontend build modernization (ADR-0016)
- ✅ Multi-agent system implementation
- ✅ Campaign and character management
- ✅ Combat system with spell casting
- ✅ Real-time multiplayer via WebSocket

**Upcoming Features:**
- User authentication and authorization
- Party management system
- Persistent combat encounters
- Enhanced NPC AI with long-term memory
- Mobile-responsive UI improvements
