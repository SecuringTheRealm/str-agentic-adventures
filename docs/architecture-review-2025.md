# Architecture Review - Agent Framework Implementation

**Date**: 2025-10-31
**Reviewer**: Claude Code
**Status**: Complete

## Executive Summary

This review examined the repository for consistency and architectural correctness, particularly focusing on the agentic framework implementation. The review found that while all unit tests pass, there are significant architectural inconsistencies between documented intent and actual implementation.

## Test Results

✅ **All Unit Tests Pass**
- 325 tests passed
- 6 tests skipped
- 33 warnings (deprecation notices, not errors)

## Critical Findings

### 1. Agent Framework Implementation Inconsistency

**Severity**: High
**Status**: Documentation vs Implementation Mismatch

#### Current State

The codebase declares a migration from Semantic Kernel to Microsoft Agent Framework (see ADR-0018), but the actual implementation is a **hybrid architecture**:

**Dependencies Declared** (`pyproject.toml:30-32`):
```toml
"azure-ai-agents>=1.0.0",
"azure-ai-projects>=1.0.0",
"azure-ai-inference>=1.0.0b1",
```

**But Implementation Uses**:
1. `kernel_setup.py` - Still fully implements Semantic Kernel
2. `agent_client_setup.py` - Implements Azure AI SDK clients (NOT Agent Framework)
3. All agents (`narrator_agent.py`, `dungeon_master_agent.py`, etc.) - Direct Azure OpenAI API calls

#### The Problem

The codebase is **not actually using Microsoft Agent Framework**. Instead, it:
- Uses Azure AI SDK's `ChatCompletionsClient` for chat completions
- Uses Azure AI SDK's `AgentsClient` (which is initialized but never used in agent implementations)
- Makes direct `azure_openai_client.chat_completion()` calls instead of using agent orchestration

#### What Microsoft Agent Framework Actually Is

From https://learn.microsoft.com/en-us/agent-framework/:

Microsoft Agent Framework provides:
- **Agent orchestration** with built-in patterns (sequential, parallel, hierarchical)
- **Agent-to-agent communication** via structured protocols
- **State management** across agent interactions
- **Tool/function calling** with agent context
- **Built-in observability** and tracing

#### What This Codebase Actually Does

The current implementation:
- ✅ Uses Azure AI SDK clients (good foundation)
- ✅ Has agent classes with defined interfaces
- ❌ Does NOT use Agent Framework's orchestration
- ❌ Does NOT use Agent Framework's communication protocols
- ❌ Does NOT use Agent Framework's state management
- ❌ Agents just make standalone OpenAI calls

#### Example: Current Agent Implementation

```python
# backend/app/agents/narrator_agent.py
class NarratorAgent:
    def __init__(self):
        chat_client = agent_client_manager.get_chat_client()
        self.azure_client = AzureOpenAIClient()  # Direct OpenAI wrapper

    async def describe_scene(self, scene_context):
        # Direct API call, NOT using Agent Framework
        response = await self.azure_client.chat_completion(
            messages=[...],
            temperature=0.75,
        )
        return response
```

#### What It Should Look Like (Microsoft Agent Framework)

```python
# Example of proper Agent Framework usage
from azure.ai.agents import Agent, AgentOrchestrator

class NarratorAgent(Agent):
    def __init__(self, orchestrator: AgentOrchestrator):
        super().__init__(name="narrator", orchestrator=orchestrator)
        self.register_tools([describe_scene, process_action])

    async def describe_scene(self, context):
        # Agent Framework handles orchestration, state, and communication
        return await self.execute_tool("describe_scene", context)
```

### 2. Semantic Kernel Still Present

**Files Still Using Semantic Kernel**:
- `backend/app/kernel_setup.py` - Full Semantic Kernel implementation
- All plugins in `backend/app/plugins/` - Reference Semantic Kernel in docstrings

**Impact**: Creates confusion about which framework is actually in use.

### 3. Deploy-PR Script Issues (FIXED)

**Issues Found and Fixed**:

#### Issue 1: Node Version Mismatch ✅ FIXED
- **File**: `.github/workflows/deploy-environment.yml:104`
- **Problem**: Used Node 20, frontend requires >=22
- **Fix**: Updated to Node 22

#### Issue 2: Missing OpenAPI Client Generation ✅ FIXED
- **File**: `.github/workflows/deploy-environment.yml:287-313`
- **Problem**: Frontend build attempted without generating API client
- **Fix**: Added OpenAPI client generation step before build:
  ```yaml
  # Wait for backend to be ready
  # Generate client from deployed backend's OpenAPI schema
  npx @openapitools/openapi-generator-cli generate \
    -i "$BACKEND_URL/openapi.json" \
    -g typescript-axios \
    -o src/api-client \
    --skip-validate-spec
  ```

## Recommendations

### Priority 1: Clarify Framework Usage in Documentation

**Action**: Update documentation to accurately reflect current implementation:
- Current implementation uses Azure AI SDK clients, NOT Agent Framework orchestration
- If true Agent Framework migration is desired, create a new ADR with migration plan
- If current approach is acceptable, update ADR-0018 to clarify "Azure AI SDK" vs "Agent Framework"

### Priority 2: Consider True Agent Framework Migration

If the goal is to actually use Microsoft Agent Framework, a significant refactor is needed:

1. **Agent Orchestration**: Implement `AgentOrchestrator` for multi-agent coordination
2. **Agent Communication**: Use framework's message passing instead of direct calls
3. **State Management**: Leverage framework's state tracking
4. **Tool Registration**: Register plugin functions as agent tools

**Estimated Effort**: Medium-High (2-3 weeks for full migration)

### Priority 3: Remove Semantic Kernel Remnants

Either:
1. Fully remove `kernel_setup.py` and Semantic Kernel references, OR
2. If keeping for backward compatibility, document why and add deprecation notices

### Priority 4: Monitor Deploy-PR Workflow

Test the fixed deploy-pr workflow on next PR to ensure:
- Node 22 works correctly
- OpenAPI client generation succeeds
- Build completes without type errors

## Architectural Debt Assessment

| Category | Severity | Impact | Effort to Fix |
|----------|----------|--------|---------------|
| Framework Inconsistency | High | Documentation/Reality Mismatch | Low (docs) or High (code) |
| Semantic Kernel Remnants | Medium | Confusion, Potential Bugs | Low |
| Deploy-PR Issues | High | Deployment Failures | Complete (FIXED) |

## Conclusion

The codebase is **functionally sound** (all tests pass) but has **architectural documentation inconsistencies**. The main issue is that the system claims to use "Microsoft Agent Framework" but actually uses "Azure AI SDK with custom agent wrappers."

**Recommended Path Forward**:
1. ✅ Deploy-PR fixes are complete
2. Update AGENTS.md and ADR-0018 to clarify current architecture
3. Decide: Keep current approach OR migrate to true Agent Framework
4. Remove Semantic Kernel references to reduce confusion

## References

- ADR-0018: Azure AI Agents Implementation
- Microsoft Agent Framework: https://learn.microsoft.com/en-us/agent-framework/
- Azure AI SDK: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-inference-readme
