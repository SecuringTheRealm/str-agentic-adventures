# Deployment Guide

This document explains how to deploy the STR Agentic Adventures application to Azure using the Azure Developer CLI (azd) and GitHub Actions.

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure OpenAI Service**: You need access to Azure OpenAI with the following models deployed:
   - GPT-4 or GPT-4o-mini for chat completion
   - text-embedding-ada-002 for embeddings
   - DALL-E 3 for image generation (optional)

## Local Development Setup

1. Install the [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
2. Clone this repository
3. Configure your environment:
   ```bash
   azd auth login
   azd env new <environment-name>
   azd env set AZURE_OPENAI_ENDPOINT <your-openai-endpoint>
   azd env set AZURE_OPENAI_API_KEY <your-openai-api-key>
   ```
4. Deploy to Azure:
   ```bash
   azd up
   ```

## GitHub Actions Deployment

### Setting Up Secrets

Configure the following secrets in your GitHub repository settings:

#### Required for Production Deployment
- `AZURE_CLIENT_ID`: Azure Service Principal Client ID
- `AZURE_TENANT_ID`: Azure Tenant ID  
- `AZURE_SUBSCRIPTION_ID`: Azure Subscription ID
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key

#### Optional Variables
- `AZURE_LOCATION`: Azure region (default: eastus)
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Chat model deployment name (default: gpt-4o-mini)
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Embedding model deployment name (default: text-embedding-ada-002)
- `AZURE_OPENAI_DALLE_DEPLOYMENT`: DALL-E deployment name (default: dall-e-3)

### Authentication Methods

#### Option 1: Federated Credentials (Recommended)
This is the most secure method using OpenID Connect:

1. Create an Azure Service Principal
2. Configure federated credentials for your GitHub repository
3. Set up the required secrets above

#### Option 2: Service Principal with Secret
If federated credentials are not available:

1. Create an Azure Service Principal with a secret
2. Set `AZURE_CREDENTIALS` secret with the complete credential JSON

### Deployment Workflows

#### Production Deployment
- **Trigger**: Push to `main` branch or manual trigger
- **Workflow**: `.github/workflows/deploy-production.yml`
- **Environment**: production
- **Resources**: Creates a production environment with all Azure resources

#### Pull Request Environments
- **Trigger**: Pull request opened/updated against `main` branch
- **Workflow**: `.github/workflows/deploy-pr.yml`
- **Environment**: development
- **Resources**: Creates a temporary environment for testing

#### Environment Cleanup
- **Trigger**: Pull request closed/merged
- **Workflow**: `.github/workflows/cleanup-pr.yml`
- **Action**: Deletes the temporary PR environment

## Azure Resources

The deployment creates the following Azure resources:

### Core Infrastructure
- **Resource Group**: Contains all resources for the environment
- **Log Analytics Workspace**: Centralized logging for monitoring
- **Container Apps Environment**: Hosts the backend application

### Application Services
- **Container App**: Hosts the Python/FastAPI backend
- **Static Web App**: Hosts the React frontend
- **Storage Account**: Stores game data and generated images

### Integration Services
- Uses your existing **Azure OpenAI Service** for AI capabilities

## Environment Configuration

### Production Environment
- **Environment Name**: `production`
- **Resource Naming**: `production-<resource>-<unique-suffix>`
- **Scaling**: Auto-scaling enabled with appropriate limits
- **Security**: HTTPS enforced, secure secrets management

### Development Environment (PR)
- **Environment Name**: `pr-<number>`
- **Resource Naming**: `pr-<number>-<resource>-<unique-suffix>`
- **Lifecycle**: Automatically created and destroyed with PRs
- **Purpose**: Testing changes before merging

## Cost Management

### Development Environments
- Use minimal resource allocations
- Automatically cleaned up to prevent cost accumulation
- Shared Azure OpenAI service to minimize AI costs

### Production Environment
- Optimized for performance and reliability
- Auto-scaling to handle traffic variations
- Monitor costs through Azure Cost Management

## Monitoring and Troubleshooting

### Application Insights
- Integrated with Container Apps for backend monitoring
- Performance metrics and error tracking
- Custom dashboards available in Azure portal

### Logs
- Container logs available in Log Analytics
- Real-time monitoring through Azure portal
- GitHub Actions provide deployment summaries

### Common Issues
1. **Azure OpenAI Access**: Ensure your subscription has access to Azure OpenAI
2. **Resource Limits**: Check subscription limits for Container Apps and Static Web Apps
3. **Permissions**: Verify the service principal has Contributor access to the subscription

## Security Considerations

1. **Secrets Management**: All sensitive data stored as GitHub secrets or Azure Key Vault
2. **Network Security**: HTTPS enforced for all endpoints
3. **Authentication**: Service principal with minimal required permissions
4. **Resource Isolation**: Each environment in separate resource groups

## Maintenance

### Regular Updates
- Update the Azure Developer CLI regularly
- Keep Docker base images updated for security
- Monitor Azure service updates and deprecations

### Backup and Recovery
- Application data stored in Azure Storage with redundancy
- Infrastructure as code allows easy recreation
- Database backups (if using Azure Database services)

## Getting Help

For deployment issues:
1. Check GitHub Actions logs for detailed error messages
2. Review Azure portal for resource status
3. Consult Azure Developer CLI documentation
4. Check Azure service health status