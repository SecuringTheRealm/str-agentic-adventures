# Multi-Platform AI Instruction Architecture

* Status: accepted
* Date: 2025-01-27

## Context and Problem Statement

The project needs to support multiple AI platforms for code assistance, including OpenAI Codex, GitHub Copilot Chat, GitHub Copilot coding agent, and GitHub Copilot code review. Each platform has different requirements for where and how coding instructions should be stored and organized. We need a unified approach that supports all platforms while avoiding instruction duplication and maintaining clear organization.

Platform requirements:
- OpenAI Codex expects coding instructions in `AGENTS.md` at the root directory
- GitHub Copilot Chat, coding agent, and code review support `.github/copilot-instructions.md`
- GitHub Copilot coding agent supports multiple `.instructions.md` files in `.github/instructions/` with `applyTo` frontmatter for targeted guidance

## Decision Drivers

* Support for multiple AI platforms with different file location requirements
* Avoid duplication of instruction content across files
* Maintain clear organization and discoverability of coding guidelines
* Provide both comprehensive and targeted guidance for different development scenarios
* Enable platform-specific optimizations while maintaining consistency
* Support domain-specific instruction files for better AI targeting (Python, TypeScript, testing, etc.)

## Considered Options

* Option 1: Single comprehensive instruction file
    * Place all instructions in one location (either root AGENTS.md or .github/copilot-instructions.md)
    * Pros: Simple structure, no duplication, easy to maintain
    * Cons: Doesn't support all platforms, large file difficult to navigate, no domain-specific targeting

* Option 2: Platform-specific instruction files with content duplication
    * Create separate complete instruction sets for each platform
    * Pros: Platform optimization, independent evolution
    * Cons: Significant content duplication, maintenance burden, inconsistency risk

* Option 3: Hierarchical multi-platform architecture (chosen)
    * Root `AGENTS.md` for OpenAI Codex pointing to comprehensive instructions
    * `.github/copilot-instructions.md` for GitHub Copilot Chat/review with full project setup
    * `.github/instructions/*.instructions.md` for targeted domain-specific guidance
    * Pros: Supports all platforms, minimal duplication, organized by domain, scalable
    * Cons: More complex file structure, requires coordination between files

## Decision Outcome

Chosen option: "Hierarchical multi-platform architecture"

Justification:
* Meets all platform requirements without compromising functionality
* Provides both comprehensive guidance (copilot-instructions.md) and targeted domain-specific instructions
* Minimizes duplication by using pointer pattern from AGENTS.md to detailed instructions
* Allows platform-specific optimizations while maintaining consistency
* Supports the project's complex multi-language, multi-framework architecture
* Enables fine-grained control over AI assistance for different development contexts

## Consequences

### Positive
* Full support for OpenAI Codex, GitHub Copilot Chat, coding agent, and code review
* Domain-specific instruction targeting improves AI assistance quality
* Clear separation of concerns between general and specialized guidance
* Scalable structure that can accommodate new AI platforms
* Reduced cognitive load with focused instruction files
* Better AI performance through targeted context and rules

### Negative
* More complex file structure requires understanding of the hierarchy
* Need to maintain consistency across multiple instruction files
* Potential for instructions to become outdated in different files
* Risk of confusion about which file to update for specific changes

### Risks and Mitigations
* Risk: Instruction inconsistency across files
  * Mitigation: Use DRY principle with references between files, regular review cycles
* Risk: Developers unsure which file to update
  * Mitigation: Clear documentation in each file about its purpose and scope
* Risk: Platform changes breaking compatibility
  * Mitigation: Monitor platform documentation, maintain flexibility in structure

## Links

* Related ADRs: None directly related
* References: 
  * [OpenAI Codex Documentation](https://platform.openai.com/docs/codex/overview)
  * [GitHub Copilot Custom Instructions](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
* Superseded by: None

## File Structure

The implemented structure includes:

- `AGENTS.md` - Root-level entry point for OpenAI Codex, points to comprehensive instructions
- `.github/copilot-instructions.md` - Complete project setup and development workflow for GitHub Copilot Chat and code review
- `.github/instructions/` - Domain-specific instruction files with `applyTo` frontmatter:
  - `general-coding.instructions.md` - Foundation rules for all code
  - `python.instructions.md` - Backend development with FastAPI and Semantic Kernel
  - `typescript-react.instructions.md` - Frontend development standards
  - `testing.instructions.md` - Comprehensive testing guidelines
  - `documentation.instructions.md` - Documentation organization and standards
  - `database.instructions.md` - Database and migration management
  - `adr.instructions.md` - Architecture Decision Record standards