# Migration Reference: Semantic Kernel → Azure AI Agents SDK

This migration is **complete**. The project now uses the Azure AI Agents SDK exclusively.

## Key Changes (Summary)

| Area | Before | After |
|------|--------|-------|
| Agent framework | `semantic-kernel` | `azure-ai-agents`, `azure-ai-projects` |
| Chat completions | `AzureChatCompletion` via Kernel | `azure_openai_client` singleton |
| Agent setup | `kernel_manager.get_kernel()` | `agent_framework_manager.create_agent()` |
| Plugins | `@kernel_function` decorator | Direct method calls |
| Observability | None | Built-in OpenTelemetry |

## Architecture Decision

See [ADR-0018](adr/0018-azure-ai-agents-sdk-adoption.md) for the full rationale, options considered, and migration consequences.

## Implementation

All agents now inherit from `AgentFrameworkManager` in `backend/app/agent_framework_base.py`. Refer to existing agent files in `backend/app/agents/` for implementation patterns.
