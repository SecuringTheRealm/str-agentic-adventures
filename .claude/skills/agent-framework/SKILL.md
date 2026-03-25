---
name: agent-framework
description: Azure AI agent creation patterns, tool registration, singleton client, fallback mode
---

# Agent Framework Patterns

## Client Access
- Use singleton `azure_openai_client` from `backend/app/azure_openai_client.py`
- Never instantiate `AzureOpenAIClient()` directly
- Uses `DefaultAzureCredential` (managed identity in Azure, `az login` locally)

## Creating Agents
- All agents use `AgentClientManager` from `backend/app/agent_client_setup.py`
- Create with `agent_client_manager.create_agent(name, instructions, model, tools, temperature)`
- Store agent references for reuse via module-level singletons

## Tool Registration
- Use `agent_client_manager.create_function_tool(name, description, parameters, callable_fn)`
- Include clear descriptions and typed parameters
- Tools are registered at agent creation time

## Fallback Mode
- All agents MUST check `azure_openai_client.is_configured()`
- When False: use deterministic game logic, never call Azure
- Wrap Azure SDK calls in try-except with context logging

## Thread Management
- Create threads with `agent_client_manager.create_thread()`
- Use threads to maintain conversation context across interactions
- One thread per game session per agent

## Architecture Decision
- See ADR-0018 for migration rationale
- SDK: `azure-ai-projects>=1.0.0,<2.0.0`
- API version: `2025-05-01`
