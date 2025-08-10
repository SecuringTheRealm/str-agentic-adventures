# Copilot Workflow Optimization with Dependency Caching

* Status: accepted
* Date: 2025-08-10

## Context and Problem Statement

The Copilot agent setup workflow was experiencing significant performance issues that impacted developer productivity and CI/CD pipeline efficiency. The original setup process required:

1. Fresh installation of Python dependencies (UV) taking ~20 seconds each time
2. Fresh installation of Node.js frontend dependencies taking ~3-4 minutes each time  
3. No caching mechanisms to preserve dependencies between runs
4. Improper workflow structure with setup steps located outside GitHub Actions workflow directory

This resulted in total setup times of 4+ minutes on every Copilot agent startup, significantly impacting developer experience and increasing CI costs. The lack of dependency caching meant that even when lock files hadn't changed, all dependencies were reinstalled from scratch.

## Decision Drivers

* **Developer Experience**: Reduce Copilot agent startup time to improve productivity
* **CI/CD Efficiency**: Minimize GitHub Actions runtime minutes and associated costs
* **Consistency**: Align dependency versions with existing CI workflows (Python 3.12, Node.js 20)
* **Reliability**: Ensure dependency caching doesn't introduce inconsistencies or stale dependencies
* **Maintainability**: Use GitHub Actions best practices for workflow structure and organization

## Considered Options

* Option 1: Keep existing non-optimized setup process
    * No changes to current workflow structure
    * Pros: No risk of introducing caching-related issues
    * Cons: Continued poor performance, high CI costs, poor developer experience

* Option 2: Implement dependency caching with GitHub Actions cache
    * Use actions/cache@v4 for Python UV dependencies and built-in npm caching for Node.js
    * Move workflow to proper .github/workflows/ directory with complete GitHub Actions structure
    * Pros: Significant performance improvement, leverages GitHub Actions best practices, maintains cache invalidation on lock file changes
    * Cons: Adds complexity, potential for cache-related debugging if issues arise

* Option 3: Use third-party caching solutions
    * Implement external caching systems or custom dependency management
    * Pros: Potentially faster than GitHub Actions cache
    * Cons: Added complexity, external dependencies, potential security concerns

## Decision Outcome

Chosen option: "Implement dependency caching with GitHub Actions cache"

Justification:
* Provides significant performance improvements (4+ minutes reduced to cached retrieval times)
* Uses GitHub Actions native caching which is well-tested and reliable
* Maintains proper cache invalidation based on lock files (pyproject.toml, uv.lock, package-lock.json)
* Aligns with industry best practices for CI/CD optimization
* Keeps dependency versions consistent with existing CI workflows
* Moves workflow to proper location with complete GitHub Actions structure

## Consequences

### Positive
* **Dramatic performance improvement**: Startup times reduced from 4+ minutes to seconds on cache hits
* **Cost reduction**: Significantly lower GitHub Actions minutes usage for Copilot workflows
* **Better developer experience**: Faster iteration cycles when working with Copilot
* **Consistency**: Python 3.12 and Node.js 20 aligned with existing CI workflows
* **Proper workflow structure**: Complete GitHub Actions workflow in correct directory location

### Negative
* **Cache complexity**: Potential debugging complexity if caching issues arise
* **Storage usage**: GitHub Actions cache storage consumption (within GitHub limits)
* **Initial cache miss**: First run still requires full dependency installation

### Risks and Mitigations
* **Risk**: Cache corruption or inconsistent dependencies
* **Mitigation**: Cache keys based on lock file hashes ensure invalidation on dependency changes
* **Risk**: Cache storage limits
* **Mitigation**: GitHub provides generous cache limits, and old caches are automatically evicted
* **Risk**: Debugging cache-related issues
* **Mitigation**: Clear cache key structure and ability to manually clear caches if needed

## Links

* Related ADRs: [0007-github-actions-cicd-pipeline.md](0007-github-actions-cicd-pipeline.md), [0013-ci-workflow-optimization.md](0013-ci-workflow-optimization.md)
* References: 
  - [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
  - [UV Caching Documentation](https://docs.astral.sh/uv/concepts/cache/)
  - [NPM CI Caching Best Practices](https://docs.npmjs.com/cli/v8/commands/npm-ci)
* Implementation: [.github/workflows/copilot-setup-steps.yml](../../.github/workflows/copilot-setup-steps.yml)