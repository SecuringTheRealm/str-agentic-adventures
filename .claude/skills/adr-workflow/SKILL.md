---
name: adr-workflow
description: Architecture Decision Record creation process and conventions
---

# ADR Workflow

## When to Write an ADR
- Technology or framework selection
- Significant architectural pattern choice
- Security or deployment strategy decisions
- NOT for trivial choices (CSS colour, variable naming)

## Create a New ADR
1. Find the next number: `ls docs/adr/*.md | tail -1`
2. Copy template: `cp docs/adr/template.md docs/adr/NNNN-short-description.md`
3. Fill in: Status, Context, Decision, Rationale, Consequences

## Format
- Filename: `NNNN-kebab-case-description.md`
- Status: `Proposed` → `Accepted` → optionally `Deprecated` or `Superseded by NNNN`
- Keep it concise: 50-100 lines typical

## Existing ADRs
- 18 ADRs covering: FastAPI, React, SQLAlchemy, Azure OpenAI, CSS Modules, OpenAPI gen, ARM templates, Container Apps, GitHub Actions, Pydantic settings, error boundaries, Alembic, Docker, scale-to-zero, fallback mode, GHCR, Log Analytics, Azure AI Agents SDK
