# Architecture Decision Records

## Overview

This directory contains Architecture Decision Records (ADRs) for the Agentic Adventures project. ADRs are used to document important architectural decisions, their context, and consequences.

## How to Use ADRs

1. Copy `template.md` to create a new ADR
2. Name the file using the format: `NNNN-title-with-hyphens.md` where NNNN is the next available number
3. Fill in all sections of the template
4. Add the ADR to the table below
5. Submit for review as part of a pull request

## Decision Log

| Number | Title | Status | Date | Description |
|--------|-------|--------|------|-------------|
| 0000 | [Using ADRs](template.md) | Accepted | 2025-06-10 | Template for architecture decisions |
| 0001 | [Use Microsoft Semantic Kernel for Multi-Agent Architecture](0001-semantic-kernel-multi-agent-framework.md) | Accepted | 2025-06-10 | Selection of Microsoft Semantic Kernel as the foundation for our multi-agent system |
| 0002 | [Specialized Multi-Agent Architecture for AI Dungeon Master](0002-specialized-multi-agent-architecture.md) | Accepted | 2025-06-10 | Approach for structuring the different AI agents in the system |
| 0003 | [Data Storage Strategy for Game State and Assets](0003-data-storage-strategy.md) | Accepted | 2025-06-10 | Strategy for storing and managing game data and assets |
| 0004 | [React and TypeScript Frontend Architecture](0004-react-typescript-frontend.md) | Accepted | 2025-06-10 | Selection of React with TypeScript for the frontend application |
| 0005 | [Azure OpenAI Integration for AI Agents](0005-azure-openai-integration.md) | Accepted | 2025-06-10 | Approach for integrating Azure OpenAI services for AI capabilities |
| 0006 | [D&D 5e Character Progression System Implementation](0006-dnd-5e-character-progression-system.md) | Accepted | 2025-06-11 | Implementation of D&D 5e leveling and progression rules |
| 0007 | [Local JSON Persistence for Prototype Data](0007-local-json-persistence.md) | Proposed | 2025-06-11 | Temporary JSON file storage for development |

## ADR Statuses

- **Proposed**: A decision has been proposed but not yet reviewed
- **Accepted**: The decision has been accepted and is being implemented
- **Rejected**: The decision was rejected
- **Deprecated**: The decision was once accepted but is no longer relevant
- **Superseded**: The decision has been replaced by a newer decision