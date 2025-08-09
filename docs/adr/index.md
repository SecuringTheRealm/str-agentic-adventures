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
| 0003 | [Data Storage Strategy for Game State and Assets](0003-data-storage-strategy.md) | Superseded | 2025-06-10 | Strategy for storing and managing game data - updated for SQLAlchemy implementation |
| 0004 | [React and TypeScript Frontend Architecture](0004-react-typescript-frontend.md) | Accepted | 2025-06-10 | Selection of React with TypeScript for the frontend application |
| 0005 | [Azure OpenAI Integration for AI Agents](0005-azure-openai-integration.md) | Accepted | 2025-06-10 | Approach for integrating Azure OpenAI services for AI capabilities |
| 0006 | [D&D 5e Character Progression System Implementation](0006-dnd-5e-character-progression-system.md) | Accepted | 2025-06-11 | Implementation of character progression mechanics |
| 0007 | [GitHub Actions CI/CD Pipeline](0007-github-actions-cicd-pipeline.md) | Accepted | 2025-06-11 | Continuous integration and deployment pipeline for automated testing and quality assurance |
| 0008 | [Multiplayer Implementation for Real-Time Collaborative Gameplay](0008-multiplayer-implementation.md) | Superseded | 2025-01-27 | Real-time multiplayer architecture - updated for Python/FastAPI compatibility |
| 0009 | [Container App Deployment Strategy](0009-container-app-deployment-strategy.md) | Accepted | 2025-06-12 | Single deployment approach to avoid duplicate container apps |
| 0010 | [Technology Review Implementation Strategy](0010-technology-review-implementation.md) | Accepted | 2025-01-27 | Comprehensive implementation of all "real implementation" comments and system enhancements |
| 0011 | [OpenAPI Client Generation for Frontend-Backend Integration](0011-openapi-client-generation.md) | Accepted | 2025-01-29 | Generate TypeScript client from FastAPI OpenAPI schema to eliminate manual API type duplication |
| 0012 | [FastAPI Lifespan Event Handler Migration](0012-fastapi-lifespan-migration.md) | Accepted | 2025-01-09 | Migration from deprecated on_event handlers to modern lifespan context manager |
| 0013 | [CI Workflow Optimization for Reduced Duplication and CI Minutes](0013-ci-workflow-optimization.md) | Accepted | 2025-08-09 | Optimization of GitHub Actions workflows to reduce CI minutes usage and improve PR feedback loops |

## ADR Statuses

- **Proposed**: A decision has been proposed but not yet reviewed
- **Accepted**: The decision has been accepted and is being implemented
- **Rejected**: The decision was rejected
- **Deprecated**: The decision was once accepted but is no longer relevant
- **Superseded**: The decision has been replaced by a newer decision