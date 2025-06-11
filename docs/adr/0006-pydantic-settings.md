# Adopt pydantic-settings for Configuration Management

* Status: accepted
* Date: 2025-06-11

## Context and Problem Statement

The backend previously used `pydantic.BaseSettings` from the `pydantic` package. With the release of pydantic v2, the recommended way to load environment variables is through the separate `pydantic-settings` package. We also need default values for testing so that the backend can create a Semantic Kernel instance without explicit environment configuration.

## Decision Drivers

* Compatibility with pydantic v2
* Simplified configuration loading from `.env` files and environment variables
* Ability to provide sensible defaults for local development and automated tests

## Considered Options

* **Continue using `pydantic.BaseSettings` from pydantic**
  * Pros: no code changes
  * Cons: deprecated approach in pydantic v2, requires extra boilerplate
* **Switch to `pydantic-settings.BaseSettings`**
  * Pros: aligns with pydantic v2, built-in support for environment variable loading
  * Cons: new dependency
* **Custom configuration loader**
  * Pros: complete control
  * Cons: more code to maintain

## Decision Outcome

Chosen option: "Switch to `pydantic-settings.BaseSettings`"

Justification:
* Provides straightforward `.env` loading and environment variable overrides
* Works seamlessly with the rest of the codebase and Semantic Kernel setup
* Minimizes custom code while keeping configuration explicit

## Consequences

### Positive
* Cleaner configuration code with defaults for tests
* Easier upgrades alongside pydantic v2

### Negative
* Additional dependency to manage

### Risks and Mitigations
* **Risk:** Missing environment variables could cause runtime errors
  * **Mitigation:** Provide default values for test environments and validate configuration at startup

## Links
* Related ADRs: [0001-semantic-kernel-multi-agent-framework.md](0001-semantic-kernel-multi-agent-framework.md)
* References: [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
