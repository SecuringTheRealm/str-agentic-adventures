# Adopt Azure AI Agents SDK for Multi-Agent Architecture

* Status: accepted
* Date: 2025-10-12

## Context and Problem Statement

The project currently uses Microsoft Semantic Kernel for multi-agent orchestration. Microsoft has evolved its AI agent offerings into the Azure AI Agents SDK, which provides production-grade agent orchestration as part of Azure AI Foundry. This new SDK offers better integration with Azure services, improved observability through OpenTelemetry, and a more robust foundation for building enterprise AI applications. We need to migrate from Semantic Kernel to Azure AI Agents SDK to ensure long-term compatibility and access to advanced agent capabilities.

## Decision Drivers

* Microsoft's strategic shift toward Azure AI Foundry as the unified AI platform
* Need for production-grade reliability and observability in agent operations
* Requirement for better Azure service integration and managed identity support
* Desire for OpenTelemetry-based agent tracing and monitoring
* Need for more deterministic agent orchestration patterns
* Compatibility with Azure's long-term AI roadmap

## Considered Options

* Option 1: Azure AI Agents SDK (azure-ai-agents, azure-ai-projects)
    * Microsoft's current production-grade agent framework integrated with Azure AI Foundry
    * Pros:
      * Native Azure AI Foundry integration for model management and deployment
      * Built-in OpenTelemetry observability for agent operations
      * Support for both API key and managed identity authentication
      * Production-ready with Azure enterprise support
      * Clear migration path from Semantic Kernel
      * Better separation of concerns between deterministic and non-deterministic workflows
    * Cons:
      * Requires migration effort from existing Semantic Kernel code
      * Team needs to learn new API patterns
      * Some plugin patterns need to be converted to tool functions

* Option 2: Continue with Semantic Kernel
    * Maintain current implementation with Microsoft Semantic Kernel
    * Pros:
      * No migration effort required
      * Team already familiar with the framework
      * Current code is working
    * Cons:
      * Microsoft is shifting focus to Azure AI Agents SDK
      * Less integration with Azure AI Foundry
      * Limited observability features compared to new SDK
      * May face deprecation or reduced support in the future

* Option 3: AutoGen Framework
    * Microsoft's multi-agent conversation framework
    * Pros:
      * Advanced multi-agent conversation capabilities
      * Good for complex agent interactions
    * Cons:
      * More focused on autonomous agent conversations
      * Less integrated with Azure services
      * Would require significant architectural changes
      * Overkill for our current use cases

## Decision Outcome

Chosen option: "Azure AI Agents SDK (azure-ai-agents, azure-ai-projects)"

Justification:
* Azure AI Agents SDK represents Microsoft's strategic direction for production AI applications
* Built-in observability through OpenTelemetry provides better debugging and monitoring
* Native Azure AI Foundry integration aligns with our Azure-first deployment strategy
* Clearer separation between deterministic workflows (game rules, dice rolls) and non-deterministic AI operations
* Production-grade features like managed identity support improve security
* Migration path is well-documented and straightforward

## Consequences

### Positive
* Access to production-grade agent orchestration with Azure enterprise support
* Built-in OpenTelemetry integration provides comprehensive agent observability
* Better alignment with Azure AI Foundry for model deployment and management
* Improved security through managed identity authentication options
* Clearer architectural patterns for deterministic vs non-deterministic operations
* Long-term compatibility with Microsoft's AI platform evolution

### Negative
* Migration effort required to convert Semantic Kernel code to new SDK
* Team needs to learn new API patterns and SDK structure
* Some existing Semantic Kernel plugins need refactoring as tools
* Temporary disruption during migration period
* Need to update documentation and developer onboarding materials

### Risks and Mitigations
* Risk: Migration introduces bugs or breaks existing functionality
  * Mitigation: Comprehensive testing at each migration step, maintain fallback mode for backward compatibility
* Risk: New SDK has learning curve that slows development
  * Mitigation: Thorough documentation, code examples, and team training sessions
* Risk: Azure AI Agents SDK may have limitations not present in Semantic Kernel
  * Mitigation: Prototype critical features early, maintain abstraction layer for potential future changes

## Status Update (2025-10-15)

- `DungeonMasterAgent` now uses the shared `AzureOpenAIClient` wrapper for both standard and streaming chat completions with automatic fallback to deterministic processing when Azure configuration is missing.
- `ArtistAgent` and `CombatCartographerAgent` guard their DALL·E integrations by checking for the shared Azure client and gracefully surfacing fallback messaging when image generation is unavailable.
- `NarratorAgent` continues to leverage `AzureOpenAIClient` for narrative completions, while `ScribeAgent` and `CombatMCAgent` rely on deterministic subsystems and required no OpenAI updates after this audit.
- Remaining gap: the multi-agent flow still needs deeper integration testing (Azure AI Agents orchestration with real threads/tools using Framework). Plan follow-up instrumentation before declaring the migration fully complete. Unclear if framework is in use.

## Links

* Supersedes: [ADR-0001 - Use Microsoft Semantic Kernel for Multi-Agent Architecture](0001-semantic-kernel-multi-agent-framework.md)
* References:
  * [Azure AI Agents SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)
  * [Azure AI Projects SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
  * [Azure AI Foundry Overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)
  * [OpenTelemetry Integration](https://opentelemetry.io/docs/languages/python/)
