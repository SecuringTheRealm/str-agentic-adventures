---
name: adr-workflow
description: "Triggers when the agent makes technology selections, architectural pattern choices, or security/deployment strategy decisions. Covers ADR creation and conventions."
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
3. Fill in all required sections (see below)

## Required Sections
- **Context** — what situation or problem prompted this decision
- **Decision Drivers** — constraints, goals, or forces shaping the choice
- **Decision** — what was decided and why
- **Consequences** — trade-offs, risks, and follow-up work

## Format
- Filename: `NNNN-kebab-case-description.md`
- Status: `Proposed` -> `Accepted` -> optionally `Deprecated` or `Superseded by NNNN`
- Keep it concise: 50-100 lines typical

## Immutability Rule
- Accepted ADRs are immutable — never edit an accepted ADR
- New decisions supersede old ones: set old status to `Superseded by NNNN`

## Existing ADRs
- 18 ADRs covering: FastAPI, React, SQLAlchemy, Azure OpenAI, CSS Modules, OpenAPI gen, ARM templates, Container Apps, GitHub Actions, Pydantic settings, error boundaries, Alembic, Docker, scale-to-zero, fallback mode, GHCR, Log Analytics, Microsoft Agent Framework
