# Migrate the LLM layer to the GA Microsoft Agent Framework (FoundryChatClient)

* Status: accepted
* Date: 2026-07-13

## Context and Problem Statement

The chat/agent layer had three independent defects (see ultracode findings F01/F02):

1. The advertised "Microsoft Agent Framework" path used the classic `azure-ai-agents`
   Threads/Runs API (`AgentsClient.threads/.messages/.runs`), which Microsoft's own
   migration guide labels *Previous*. It was never configured (`AZURE_AI_PROJECT_ENDPOINT`
   was set nowhere) and was broken even when configured (`await messages.list()` on an
   `AsyncItemPaged`), so 100% of production chat silently bypassed it.
2. All real chat went through a hand-rolled `AzureOpenAIClient` wrapper on the beta
   `azure-ai-inference` SDK, which is deprecated and retires on 2026-08-26.
3. The `azure-ai-inference` `ChatCompletionsClient` was instantiated only to be used as a
   boolean "configured?" flag; every completion actually ran through `AsyncAzureOpenAI`.

We needed one supported runtime chat path, config-based availability, per-agent model
selection, and a circuit breaker that guards the calls that actually reach Azure.

## Decision Drivers

* `azure-ai-inference` retires 2026-08-26 — a hard external deadline.
* The classic Threads/Runs SDK pattern is superseded by the Responses pattern.
* Project rule: every agent must keep working with Azure unconfigured (deterministic
  fallback); CI has no secrets.
* Lazy-senior bias: fewest moving parts, no model-router abstraction, delete dead code.

## Considered Options

* Option 1: Bump `azure-ai-projects` to 2.x and rewrite onto the raw Conversations/
  Responses SDK. Pros: no new top-level dependency. Cons: still hand-rolling the agent
  loop; no provider portability; more plumbing than the framework.
* Option 2: Adopt the GA Microsoft Agent Framework (`agent-framework-foundry`) with
  `FoundryChatClient` against the Foundry project endpoint. Pros: GA (v1.11), first-party
  agent loop + tool + streaming surface, single chat path, provider-portable. Cons: adds
  the `agent-framework-*` packages; pulls `azure-ai-projects>=2.2` and `openai>=2`.
* Option 3: Keep `AsyncAzureOpenAI` for chat and just delete the broken SDK path. Pros:
  smallest diff. Cons: leaves us on a bespoke wrapper and ignores the framework the repo
  advertises; no forward path to hosted agents/tools.

## Decision Outcome

Chosen option: **Option 2 — Microsoft Agent Framework `FoundryChatClient`.**

* `agent_client_setup.py` now owns a single chat runtime: a cached `FoundryChatClient`
  (`project_endpoint` + `DefaultAzureCredential`) exposing `chat_completion` /
  `chat_completion_stream`. Chat-driven agents point `self.azure_client` at the manager.
* Availability is config-based: `settings.is_foundry_configured()` /
  `is_azure_openai_configured()` — no client instantiation just to probe configuration.
* `azure_openai_client.py` is now an images-only helper on the sanctioned `openai` SDK
  (`AsyncAzureOpenAI.images.generate`) for the gpt-image-1 family (default
  `gpt-image-1-mini`, api-version `2025-04-01-preview`).
* Per-agent model selection (F03) is a single `deployment_setting` class attribute plus
  `AZURE_OPENAI_{DM,NARRATOR,COMBAT}_DEPLOYMENT` env vars that default to the main chat
  deployment via `Settings.deployment_for()`. No router.
* The shared `pybreaker` circuit breaker wraps the real Azure calls (chat + image), so
  `/health/dependencies` reflects reality.
* Deleted: the classic Threads/Runs plumbing, `azure-ai-inference`, the never-invoked SDK
  toolsets/`create_thread_and_process_run`/legacy `_get_sdk_tools`, and the 10 orphaned
  Semantic-Kernel-era plugin instances.

## Consequences

### Positive
* One supported, GA chat path; no dependency on a beta SDK retiring in weeks.
* `/health/dependencies` breaker state tracks the calls that actually reach Azure.
* Per-agent model tuning without a router; deterministic fallback preserved for CI.
* ~1,500 lines of dead/broken agent plumbing and orphaned plugins removed.

### Negative
* Adds the `agent-framework-*` packages and forces `azure-ai-projects>=2.2` and
  `openai>=2`.
* Foundry agent tool-calling (function tools registered on the agent) is not yet wired —
  agents still run deterministic tool logic in Python.

### Risks and Mitigations
* Framework API churn on non-GA sub-packages — mitigated by using only the GA
  `FoundryChatClient` surface.
* Streaming path is lightly breaker-guarded (open-check only) — acceptable; failures fall
  back to deterministic narration.

## Links

* Related ADRs: supersedes-in-part [ADR-0018](0018-azure-ai-agents-sdk-adoption.md)
  (azure-ai-agents SDK adoption).
* References:
  * https://learn.microsoft.com/agent-framework/agents/providers/microsoft-foundry
  * https://learn.microsoft.com/azure/foundry/how-to/model-inference-to-openai-migration
  * https://pypi.org/project/agent-framework-foundry/
