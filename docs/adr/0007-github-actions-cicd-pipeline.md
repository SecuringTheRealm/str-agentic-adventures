# ADR 0007: GitHub Actions CI/CD Pipeline

## Status
Accepted

## Date
2025-06-11

## Context

The AI Dungeon Master project requires a robust continuous integration and deployment (CI/CD) pipeline to ensure code quality, catch regressions early, and maintain system stability as the codebase evolves. The project has both frontend (React/TypeScript) and backend (Python/FastAPI) components that need automated testing and validation.

## Decision

We will implement a GitHub Actions-based CI/CD pipeline that:

1. **Runs on Pull Requests and Main Branch Pushes**: Ensures all changes are validated before merging
2. **Frontend Testing**: Runs Vitest tests for all React components and utilities
3. **Backend Testing**: Runs comprehensive structure validation, API compatibility tests, and integration tests
4. **Build Validation**: Ensures both frontend and backend can build successfully
5. **API Compatibility Checking**: Validates that frontend API calls match backend endpoints
6. **Syntax and Structure Validation**: Ensures code quality without requiring external dependencies in CI

### Pipeline Structure

```yaml
- Frontend Tests Job: Node.js 18, npm ci, npm test, npm build
- Backend Tests Job: Python 3.12, structure validation, API compatibility tests
- Integration Check Job: Combined validation of frontend-backend compatibility
```

### Test Strategy

- **Frontend**: Component tests, API integration tests, build validation
- **Backend**: Structure validation, syntax checking, API endpoint coverage, model compatibility
- **Integration**: Cross-component validation, API mapping verification

## Alternatives Considered

1. **Jenkins**: More complex setup, requires infrastructure management
2. **GitLab CI**: Would require migrating repositories
3. **Azure DevOps**: Good integration with Azure services but adds complexity
4. **CircleCI**: Third-party service with additional costs

## Consequences

### Positive
- Automated quality assurance on every pull request
- Early detection of API compatibility issues
- Consistent build and test environment
- Integration with GitHub ecosystem
- No additional infrastructure costs
- Prevents regressions in critical functionality

### Negative
- CI execution time adds to pull request review cycle
- GitHub Actions usage counts against organizational limits
- Requires maintenance of CI configuration

### Implementation Notes
- Uses legacy-peer-deps for frontend due to dependency conflicts
- Backend tests run without external dependencies (pydantic, etc.) for faster execution
- Structure validation ensures architectural compliance
- API compatibility tests verify frontend-backend integration

## Related ADRs
- ADR 0004: React and TypeScript Frontend Architecture
- ADR 0001: Microsoft Semantic Kernel for Multi-Agent Architecture (testing integration)
- ADR 0005: Azure OpenAI Integration (API testing considerations)

## Review Notes
This ADR addresses the integration review requirement for ensuring "GitHub actions workflow is setup to run on pull requests, to run the frontend and backend test suites on pull requests, so that future changes don't break the system."