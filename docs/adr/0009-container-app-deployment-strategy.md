# ADR-0009: Container App Deployment Strategy

## Status
Accepted

## Context

During infrastructure review, we discovered that our deployment pipeline was creating duplicate container apps for the backend service:

1. **Bicep Infrastructure**: Created a container app with a placeholder image
2. **GitHub Actions Workflow**: Created a separate container app with the actual application code

This resulted in:
- Resource waste (two container apps running simultaneously)
- Configuration confusion (different naming patterns)
- Deployment complexity (managing two separate deployments)
- Potential frontend routing issues (unclear which backend to target)

## Decision

We will use a **single deployment strategy** where:

1. **Infrastructure (Bicep)** provisions only the foundational resources:
   - Container Apps Environment
   - Storage Account
   - Log Analytics Workspace
   - Static Web App

2. **Application Deployment (GitHub Actions)** handles the container app creation and code deployment:
   - Uses `az containerapp up` to create/update the backend container app
   - Deploys the latest application code directly from source
   - Configures all environment variables and secrets
   - Uses consistent naming: `production-backend`

## Consequences

### Positive
- **Single Source of Truth**: Only one container app per environment
- **Faster Deployments**: No need to update Bicep templates for application changes
- **Consistent Configuration**: All app settings managed in one place
- **Cost Efficient**: No duplicate resources

### Negative
- **Manual Cleanup**: If workflow fails, container app might need manual cleanup
- **Dependency Order**: Container app creation depends on infrastructure being deployed first
- **Name Conflicts**: Need to ensure container app names don't conflict with Bicep naming

### Mitigation
- Use consistent naming patterns across infrastructure and deployment scripts
- Add proper error handling in deployment workflows
- Include container app status checks in deployment summary

## Implementation Notes

1. **Created Reusable Workflows**: 
   - `deploy-environment.yml`: Common deployment logic for both production and PR environments
   - `cleanup-environment.yml`: Common cleanup logic for PR environments
   
2. **Refactored Existing Workflows**:
   - `deploy-production.yml`: Now calls reusable workflow with production-specific parameters
   - `deploy-pr.yml`: Now calls reusable workflow with PR-specific parameters  
   - `cleanup-pr.yml`: Now calls reusable cleanup workflow

3. **Removed Code Duplication**:
   - Eliminated ~200 lines of duplicate code between production and PR workflows
   - Single source of truth for deployment logic
   - Consistent error handling and logging across environments

4. **Enhanced Container App Management**:
   - Automatic unique naming for PR environments using hash tokens
   - Proper cleanup of CLI-deployed container apps before Bicep stack deletion
   - Consistent storage account integration across all environments

5. **Preserved Existing Workflows**: Original workflows backed up as `-old.yml` files

## Container App Deployment & Cleanup Strategy

### Deployment Process
1. **Infrastructure Provisioning** (Bicep): Creates foundation resources
2. **Container App Deployment** (Azure CLI): Deploys application code via `az containerapp up`
3. **Frontend Deployment** (Static Web Apps): Builds and deploys React application

### Cleanup Process  
1. **Manual Container App Deletion**: Removes CLI-deployed container apps
2. **Deployment Stack Cleanup**: Removes Bicep-managed infrastructure resources
3. **Timeout & Error Handling**: Graceful handling of cleanup failures

### Benefits of Reusable Workflows
- **Maintainability**: Changes to deployment logic only need to be made once
- **Consistency**: Identical deployment process for production and PR environments  
- **Testing**: PR environments provide exact replica of production deployment
- **Reliability**: Centralized error handling and timeout management

## Related ADRs
- [ADR-0007: GitHub Actions CI/CD Pipeline](0007-github-actions-cicd-pipeline.md)
- [ADR-0002: Specialized Multi-Agent Architecture](0002-specialized-multi-agent-architecture.md)
