# Use Microsoft Semantic Kernel for Multi-Agent Architecture

* Status: accepted
* Date: 2025-06-10

## Context and Problem Statement

The AI Dungeon Master project requires a robust framework for implementing a multi-agent system where specialized AI agents work together to create a cohesive tabletop RPG experience. We need a framework that supports agent communication, orchestration, memory management, and integration with Azure OpenAI services.

## Decision Drivers

* Need for a multi-agent architecture where specialized agents handle different aspects of the game
* Requirement for seamless integration with Azure OpenAI LLMs
* Need for plugins to enable data storage and retrieval
* Need for flexible agent communication and orchestration
* Support for Python backend and TypeScript frontend

## Considered Options

* Option 1: Microsoft Semantic Kernel
    * Full-featured framework for building AI applications with plugin support
    * Pros: 
      * Native integration with Azure OpenAI
      * Support for plugins ("skills") to extend LLM functionality
      * Connectors for various data sources
      * Support for both Python and TypeScript
      * Memory management capabilities
    * Cons: 
      * Relatively new framework, still evolving
      * Learning curve for complex multi-agent scenarios

* Option 2: LangChain
    * Popular framework for chaining LLM operations
    * Pros: 
      * Large community and extensive documentation
      * Multiple connectors and tools
      * Support for Python and TypeScript
    * Cons: 
      * Less native integration with Azure services
      * Agent communication requires more custom development
      * Not purpose-built for complex multi-agent orchestration

* Option 3: Custom Agent Framework
    * Build our own framework specifically for the project
    * Pros: 
      * Complete control over implementation details
      * Tailored to our specific requirements
    * Cons: 
      * Significant development overhead
      * Need to reinvent solutions to common problems
      * Maintenance burden

## Decision Outcome

Chosen option: "Microsoft Semantic Kernel"

Justification:
* Semantic Kernel's design aligns well with our multi-agent architecture requirements
* Native integration with Azure OpenAI reduces integration complexity
* Plugin system fits our need for specialized agent functions
* Support for both Python and TypeScript allows for consistent development across backend and frontend
* Memory management capabilities support our need for maintaining game state

## Consequences

### Positive
* Simplified integration with Azure OpenAI endpoints
* Built-in support for plugins will accelerate development
* Memory and state management features will help implement game state persistence
* Ability to use the same framework across backend and frontend

### Negative
* Team will need to learn the Semantic Kernel framework
* May encounter limitations or bugs in a relatively new framework
* Some custom functionality may still need to be developed

### Risks and Mitigations
* Risk: Framework evolves rapidly, causing breaking changes
  * Mitigation: Pin to specific versions and thoroughly test before upgrading
* Risk: Documentation gaps for complex multi-agent scenarios
  * Mitigation: Establish direct connections with Microsoft's Semantic Kernel team for support

## Links

* References: [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)
