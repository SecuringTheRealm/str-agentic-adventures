---
applyTo: "**/test*/**,**/*test*"
---

# Testing Guidelines and Best Practices

Apply the [general coding guidelines](./general-coding.instructions.md) to all test code.

## Core Testing Principles

### Test Integrity and Regression Prevention

- **NEVER rewrite tests just to make them pass** - Always investigate and fix the underlying issue first
- If a test fails after code changes, the problem is usually in the code, not the test
- Only adjust tests if they were incorrect, out of date, or testing the wrong behavior
- Preserve test integrity to catch real regressions and maintain code quality

### Test Coverage Discipline

- **New features MUST include tests** - No feature is complete without proper test coverage
- **Failing tests MUST be addressed** by fixing code logic, not by changing the test
- Follow existing coverage thresholds specified in project configuration
- Never commit focused tests (`.only`, `.skip`) or disable tests without justification

## Testing Tools and Structure

### Backend Testing (Python)

- Use **Pytest** for unit tests and integration tests
- Use **pytest-asyncio** for async test functions
- Mock external systems (Azure OpenAI, databases, APIs) using **pytest-mock**
- Place test files adjacent to code or in `tests/` directory
- Name test files with `test_*.py` or `*_test.py` pattern

### Frontend Testing (TypeScript/React)

- Use **Vitest** for unit tests
- Use **@testing-library/react** for component tests  
- Use **Playwright** for browser end-to-end tests
- Follow coverage thresholds defined in `vitest.config.ts`
- Place unit/component tests in `__tests__/` or end with `.test.ts[x]`
- Place E2E specs in `e2e/` and end with `.spec.ts`

## Test Writing Best Practices

### Test Organization

- Group related tests using `describe` blocks
- Use descriptive test names that explain the behavior being tested
- Follow the **Arrange-Act-Assert** pattern
- Keep tests focused on a single behavior or outcome

### Test Quality Standards

- **Keep tests deterministic** - Avoid real time, randomness, and live network calls
- **Mock external dependencies** but not the unit under test
- Use **msw** for HTTP mocks in unit/component tests
- Prefer behavioral assertions over snapshot tests (unless output is truly static)
- Include edge cases and error scenarios in test coverage

### AI-Specific Testing

- Use deterministic outputs for reproducible AI testing
- Mock AI service responses for consistent test results
- Test failure scenarios and timeout handling
- Validate prompt inputs and outputs
- Include performance benchmarks for AI agent response times

## Test Failure Resolution Process

### When Tests Fail

1. **Investigate the root cause** - Don't immediately assume the test is wrong
2. **Check if your code changes broke existing functionality**
3. **Verify the test was testing the correct behavior originally**
4. **Fix the code issue** if the test was correct
5. **Update the test** only if it was testing incorrect behavior or is outdated

### Acceptable Reasons to Modify Tests

- **API contract changes** - When intentionally changing interfaces
- **Behavior changes** - When intentionally modifying application behavior  
- **Test bugs** - When the test itself has logical errors
- **Outdated mocks** - When external service contracts change

### Unacceptable Test Modifications

- Changing assertions just to make tests pass
- Removing test cases without understanding why they fail
- Loosening test conditions to avoid dealing with failures
- Disabling tests instead of fixing underlying issues

## Testing Documentation

### Test Documentation Requirements

- Document complex test setups and mock configurations
- Include examples of proper test patterns for new contributors
- Maintain troubleshooting guides for common test failures
- Document test data factories and fixtures

### Coverage Reporting

- Generate coverage reports in both `lcov` and `html` formats
- Include coverage metrics in CI/CD pipeline
- Exclude test files themselves from coverage calculations
- Monitor coverage trends and prevent regressions

## Integration with CI/CD

### Continuous Testing

- All tests must pass before code can be merged
- Run tests automatically on pull requests
- Include both unit tests and integration tests in CI pipeline
- Run E2E tests on staging environments

### Test Performance

- Keep test execution time reasonable (< 5 minutes for unit tests)
- Parallelize test execution where possible
- Use test caching to speed up repeated runs
- Monitor and optimize slow-running tests