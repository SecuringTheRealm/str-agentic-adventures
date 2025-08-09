# CI Workflow Optimization for Reduced Duplication and CI Minutes

* Status: Accepted
* Date: 2025-08-09

## Context and Problem Statement

The project's GitHub Actions CI/CD setup was running overlapping tests across multiple workflows (ci.yml, unit-tests.yml, integration-tests.yml, e2e-tests.yml), causing redundant executions and increased GitHub Action minutes usage. Key issues identified:

- Duplicate frontend and backend tests executed across ci.yml, unit-tests.yml, and integration-tests.yml
- Slow integration and E2E tests unnecessarily triggered on every PR
- Redundant frontend build steps between test and deploy workflows  
- Duplicate and outdated test scripts in the backend directory, outside standard testing folders
- Backend structure validation running in multiple workflows
- No clear test categorization leading to inefficient test execution

This was resulting in excessive CI minutes consumption and slower PR feedback loops due to running comprehensive tests on every PR.

## Decision Drivers

* Need to reduce GitHub Actions CI minutes usage for cost optimization
* Requirement for faster PR feedback loops with focused testing
* Maintain comprehensive testing coverage on main branch deployments
* Eliminate redundant test execution across workflows
* Improve test organization and categorization
* Simplify CI maintenance and debugging

## Considered Options

* Option 1: Keep all existing workflows but optimize triggers
    * Minimal changes to existing structure
    * Pros: Low risk, maintains existing patterns
    * Cons: Still has duplication, complex trigger logic

* Option 2: Completely consolidate to single workflow
    * Single workflow handling all test types
    * Pros: No duplication, simple to understand
    * Cons: Loss of granular control, harder to debug failures

* Option 3: Deprecate ci.yml and optimize dedicated test workflows
    * Dedicated workflows for unit, integration, and E2E tests with optimized triggers
    * Pros: Clear separation of concerns, optimized triggers, maintains granular control
    * Cons: Requires more coordination between workflows

## Decision Outcome

Chosen option: "Deprecate ci.yml and optimize dedicated test workflows"

Justification:
* Provides clear separation between fast unit tests (every PR) and comprehensive tests (main branch only)
* Eliminates redundant test execution while maintaining thorough coverage
* Allows for granular control and easier debugging of specific test types
* Enables optimal trigger patterns for different test categories
* Maintains flexibility for future workflow adjustments

## Consequences

### Positive
* Significantly reduced GitHub Actions CI minutes usage
* Faster PR feedback loops with prioritized unit tests
* Maintained comprehensive testing coverage during main branch validation
* Clearer test categorization with pytest markers (@pytest.mark.unit, @pytest.mark.integration, @pytest.mark.slow)
* Simplified test maintenance with all tests in standard directories
* Eliminated duplicate structure validation across workflows

### Negative
* Requires developers to understand the new trigger patterns
* Integration and E2E tests no longer run on every PR (manual dispatch available for high-risk PRs)
* Additional complexity in test marking and categorization

### Risks and Mitigations
* Risk: Integration issues might be caught later in main branch
  * Mitigation: Manual workflow dispatch available for high-risk PRs, nightly comprehensive testing
* Risk: Developers might miss integration test failures
  * Mitigation: Clear documentation of when to manually trigger comprehensive tests
* Risk: Test categorization might be inconsistent
  * Mitigation: Clear guidelines and examples in project documentation

## Implementation Details

### Workflow Changes
- **ci.yml**: Deprecated to minimal health check on main pushes only
- **unit-tests.yml**: Enhanced as primary PR feedback loop with unit tests and structure validation
- **integration-tests.yml**: Optimized to run only on main push, nightly, and manual dispatch
- **e2e-tests.yml**: Optimized to run only on main push, nightly, and manual dispatch

### Test Organization
- Moved orphaned test files from backend/ root to backend/tests/
- Removed 7 outdated/duplicate test files
- Added proper pytest markers for test categorization
- Consolidated structure validation in unit tests (removing duplication)

### Test Filtering
- Unit tests: `pytest -m "unit or not slow"` for fast PR feedback
- Integration tests: `pytest -m "integration or slow"` for comprehensive validation

## Links

* Related ADRs: [0007-github-actions-cicd-pipeline.md](0007-github-actions-cicd-pipeline.md)
* References: GitHub Issue #344 - Optimisation of CI Test Workflows
* Implementation: PR implementing these changes