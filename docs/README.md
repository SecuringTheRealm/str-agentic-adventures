# Documentation Index

**Project:** Securing the Realm – Agentic Adventures
**Stack:** React 19 + TypeScript (frontend) · Python 3.12 + FastAPI + Azure AI Agents SDK (backend)
**Deployment:** Azure Container Apps · PostgreSQL (prod) / SQLite (dev)

---

## Getting Started

New to this project? Start here:

1. [BUILD.md](user/BUILD.md) — local development environment setup
2. [architecture.md](architecture.md) — system design and agent framework overview
3. [prd.md](prd.md) — product requirements and vision
4. [adr/index.md](adr/index.md) — architectural decisions

---

## Directory Structure

### `/user/`
User-facing guides:
- [BUILD.md](user/BUILD.md) - Build system and development setup guide
- [FRONTEND.md](user/FRONTEND.md) - Frontend development guide

### `/specs/`
Technical specifications:
- [TESTING_STRATEGY.md](specs/TESTING_STRATEGY.md) - Test organization, patterns, and strategy
- [OPENAPI_CLIENT.md](specs/OPENAPI_CLIENT.md) - API client generation and usage
- [E2E_TEST_SUMMARY.md](specs/E2E_TEST_SUMMARY.md) - End-to-end testing results

### `/reference/`
Reference materials:
- [srd-5.2.1.md](reference/srd-5.2.1.md) - Complete D&D 5e SRD (CC-BY-4.0)
- [SRD_COMPLIANCE_SUMMARY.md](reference/SRD_COMPLIANCE_SUMMARY.md) - SRD compliance summary
- [CONTAINER_OPTIMIZATION.md](reference/CONTAINER_OPTIMIZATION.md) - Deployment optimization guide

### `/adr/`
Architecture Decision Records — 19 ADRs documenting all major technical decisions:
- [index.md](adr/index.md) - Full ADR index with descriptions
- Key decisions: [ADR-0018](adr/0018-azure-ai-agents-sdk-adoption.md) (current agent SDK), [ADR-0011](adr/0011-openapi-client-generation.md) (OpenAPI client), [ADR-0019](adr/0019-api-prefix-configuration.md) (API prefix)

---

## Root Documents

| Document | Purpose |
|----------|---------|
| [prd.md](prd.md) | Product requirements and vision |
| [architecture.md](architecture.md) | System architecture and design |
| [deployment.md](deployment.md) | Production deployment instructions |
| [AZURE_OPENAI_REQUIREMENTS.md](AZURE_OPENAI_REQUIREMENTS.md) | Azure AI configuration guide |
| [api-contracts-backend.md](api-contracts-backend.md) | REST and WebSocket API contracts |
| [data-models-backend.md](data-models-backend.md) | Database schema and ORM models |
| [migration-guide-azure-ai-sdk.md](migration-guide-azure-ai-sdk.md) | Semantic Kernel → Azure AI SDK migration reference |
| [contributions.md](contributions.md) | Open source acknowledgements |

---

## Agent & Coding Guidelines

See [../AGENTS.md](../AGENTS.md) for repository-wide coding standards, security guardrails, and AI agent implementation guidelines.
