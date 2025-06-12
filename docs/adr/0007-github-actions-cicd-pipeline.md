# ADR 0007: GitHub Actions CI/CD Pipeline

## Status
Accepted

## Date
2025-06-11 (Updated: 2025-06-12)

## Context

The AI Dungeon Master project requires a robust continuous integration and deployment (CI/CD) pipeline to ensure code quality, catch regressions early, and maintain system stability as the codebase evolves. The project has both frontend (React/TypeScript) and backend (Python/FastAPI) components that need automated testing and validation.

As the project has evolved, the CI/CD requirements have expanded beyond basic testing to include:
- Full Azure deployment automation
- PR environment management for isolated testing
- Infrastructure provisioning with Azure Bicep
- Multi-environment deployment workflows
- Path-based optimization to reduce unnecessary job execution

## Decision

We will implement a comprehensive GitHub Actions-based CI/CD pipeline that:

1. **Intelligent Change Detection**: Uses path-based filtering to only run relevant jobs when specific code areas change
2. **Continuous Integration**: Runs on pull requests and main branch pushes with comprehensive testing
3. **Frontend Testing**: Runs Vitest tests for all React components and utilities with build validation
4. **Backend Testing**: Runs extensive test suite including structure validation, API compatibility, end-to-end workflows, and ADR compliance
5. **Integration Validation**: Ensures frontend-backend API compatibility and cross-component validation
6. **Automated Deployment**: Full deployment automation to Azure with infrastructure provisioning
7. **PR Environment Management**: Creates temporary Azure environments for each pull request
8. **Environment Cleanup**: Automatically removes PR environments when pull requests are closed

### Pipeline Structure

```yaml
# CI Pipeline (ci.yml)
- Change Detection Job: Determines which components have changed (frontend/backend/integration)
- Frontend Tests Job: Node.js 18, npm ci --legacy-peer-deps, vitest --run, npm build
  - Conditional execution: only runs when frontend/ changes
- Backend Tests Job: Python 3.12, comprehensive test suite including:
  - Structure validation and syntax checking
  - API compatibility and mapping tests  
  - End-to-end workflow testing
  - Component integration testing
  - ADR compliance validation
  - Custom test execution without external dependencies
  - Conditional execution: only runs when backend/ changes
- Integration Check Job: Cross-component validation when both frontend and backend change
  - Waits for frontend and backend jobs to complete
  - Validates API model compatibility

# Deployment Pipeline (deploy-production.yml)
- Production Deployment: Triggered by pushes to main branch
  - Azure authentication (federated credentials or service principal)
  - Infrastructure deployment using Azure Bicep deployment stacks
  - Backend container deployment to Azure Container Apps
  - Frontend deployment to Azure Static Web Apps
  - Environment configuration and secrets management

# PR Environment Pipeline (deploy-pr.yml)
- PR Environment Creation: Triggered by PR events targeting main
  - Creates isolated Azure environment named "pr-{PR_NUMBER}"
  - Deploys both frontend and backend for testing
  - Comments deployment URLs on pull request

# Environment Cleanup (cleanup-pr.yml)
- Automatic cleanup when PRs are closed/merged
- Removes Azure resources to prevent cost accumulation
```

### Test Strategy

- **Frontend**: Component tests with Vitest, API integration tests, build validation, TypeScript compilation
- **Backend**: Comprehensive test suite (62+ tests) covering:
  - Pydantic model validation and serialization
  - Agent interface contracts and mocking
  - API compatibility between frontend and backend
  - End-to-end workflow testing (character creation, campaign creation, player input, image generation)
  - Component integration testing (API routes, model field consistency, agent integration)
  - Project structure validation and Python syntax checking
  - ADR implementation compliance verification
- **Integration**: Cross-component API mapping validation, model compatibility checks
- **Deployment**: Infrastructure validation, application health checks, deployment verification

### Deployment Strategy

- **Production Environment**: Automatic deployment on main branch pushes
  - Azure Container Apps for backend (FastAPI application)
  - Azure Static Web Apps for frontend (React application)
  - Azure Storage for file and image storage
  - Integration with existing Azure AI Foundry project
- **Development Environments**: Temporary PR environments for testing
  - Named "pr-{PR_NUMBER}" for isolation
  - Full deployment including infrastructure provisioning
  - Automatic cleanup on PR closure
- **Infrastructure as Code**: Azure Bicep templates for consistent deployments
  - Deployment stacks for managed resource lifecycle
  - Environment-specific configuration
  - Secrets management with Azure Key Vault integration

## Alternatives Considered

1. **Jenkins**: More complex setup, requires infrastructure management, additional security considerations
2. **GitLab CI**: Would require migrating repositories and learning new platform
3. **Azure DevOps**: Good integration with Azure services but adds complexity and requires additional Microsoft tooling
4. **CircleCI**: Third-party service with additional costs and external dependencies
5. **Manual Deployment**: Considered but rejected due to risk of human error and inconsistent deployments
6. **Azure Developer CLI (azd) only**: Simpler but lacks PR environment management and automated CI integration

## Consequences

### Positive
- **Automated Quality Assurance**: Every pull request is automatically tested with 62+ backend tests and comprehensive frontend testing
- **Early Detection**: API compatibility issues and regressions caught before merging
- **Consistent Environments**: Automated infrastructure provisioning ensures deployment consistency
- **Cost Optimization**: Path-based change detection reduces unnecessary job execution
- **PR Environment Isolation**: Each pull request gets its own Azure environment for testing
- **Zero-Downtime Deployment**: Automated deployment to Azure with infrastructure as code
- **Integration with GitHub Ecosystem**: Native GitHub Actions with excellent visibility and control
- **Flexible Authentication**: Supports both federated credentials and service principal authentication
- **Comprehensive Testing**: Includes ADR compliance, API compatibility, and end-to-end workflow validation
- **No Additional Infrastructure Costs**: Uses GitHub Actions and Azure resources only when needed

### Negative
- **Increased Complexity**: Multiple workflows and deployment strategies require maintenance
- **CI Execution Time**: Comprehensive testing adds to pull request review cycle (typically 2-5 minutes)
- **GitHub Actions Usage**: Counts against organizational limits (mitigated by conditional execution)
- **Azure Costs**: PR environments consume Azure resources (mitigated by automatic cleanup)
- **Dependency on Azure**: Deployment pipeline tightly coupled to Azure services
- **Learning Curve**: Team needs to understand Azure Bicep, Container Apps, and Static Web Apps

### Implementation Notes
- **Legacy Peer Dependencies**: Frontend uses `--legacy-peer-deps` due to React ecosystem dependency conflicts
- **Dependency-Free Backend Testing**: Backend tests run without external dependencies (Azure OpenAI, databases) for faster, more reliable execution
- **Custom Test Execution**: Uses inline Python execution instead of pytest for better control and CI optimization
- **Path-Based Optimization**: Frontend and backend jobs only run when relevant files change
- **Deployment Stack Management**: Uses Azure deployment stacks for consistent resource lifecycle management
- **Environment Variable Management**: Secure handling of Azure OpenAI endpoints and API keys
- **Automatic Cleanup**: PR environments are automatically deleted to prevent resource accumulation
- **Error Handling**: Comprehensive error handling and reporting for deployment failures

## Related ADRs
- ADR 0004: React and TypeScript Frontend Architecture (CI testing implementation)
- ADR 0001: Microsoft Semantic Kernel for Multi-Agent Architecture (testing integration and deployment)
- ADR 0005: Azure OpenAI Integration (API testing considerations and deployment configuration)
- ADR 0003: Data Storage Architecture (deployment and persistence considerations)

## Review Notes
This ADR addresses the integration review requirement for ensuring "GitHub actions workflow is setup to run on pull requests, to run the frontend and backend test suites on pull requests, so that future changes don't break the system."

**Current Implementation Status**: Fully implemented and operational
- ✅ Comprehensive CI pipeline with 62+ backend tests and frontend test suite
- ✅ Production deployment automation to Azure Container Apps and Static Web Apps  
- ✅ PR environment management with automatic cleanup
- ✅ Path-based optimization for efficient resource usage
- ✅ ADR compliance testing ensures architectural decisions are properly implemented
- ✅ Infrastructure as Code with Azure Bicep deployment stacks

**Workflow Files**:
- `.github/workflows/ci.yml`: Main CI pipeline with testing and validation
- `.github/workflows/deploy-production.yml`: Production deployment automation  
- `.github/workflows/deploy-pr.yml`: PR environment creation and deployment
- `.github/workflows/cleanup-pr.yml`: Automatic PR environment cleanup