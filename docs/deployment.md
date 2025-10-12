# Deployment Guide

This document explains how to deploy the STR Agentic Adventures application to Azure using the Azure Developer CLI (azd) and GitHub Actions.

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure AI Foundry Project**: You need access to Azure AI Foundry with the following models deployed:
   - GPT-4 or GPT-4o-mini for chat completion
   - text-embedding-ada-002 for embeddings
   - DALL-E 3 for image generation (optional)

> **Getting Started with Azure AI Foundry**: Visit [ai.azure.com](https://ai.azure.com) to create your project and deploy the required OpenAI models. Azure AI Foundry provides a unified platform for managing Azure OpenAI services and is the recommended way to access OpenAI models in Azure.

## Local Development Setup

### Prerequisites

- **Python 3.11 or higher**
- **Node.js 18 or higher**
- **Azure CLI** (for authentication and deployment)
- **Azure AI Foundry project** with deployed models

### Step-by-Step Setup

1. **Install the Azure Developer CLI**:
   ```bash
   # Download and install azd
   # See: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?WT.mc_id=AI-MVP-5004204
   ```

2. **Clone this repository**:
   ```bash
   git clone https://github.com/SecuringTheRealm/str-agentic-adventures.git
   cd str-agentic-adventures
   ```

3. **Set up Azure AI Foundry credentials**:
   - Visit [Azure AI Foundry](https://ai.azure.com)
   - Create or select an existing project
   - Deploy required models (GPT-4o-mini, text-embedding-ada-002, DALL-E 3)
   - Note your project endpoint and API key from Project Settings

4. **Configure your local environment**:
   ```bash
   # Set up backend environment
   cd backend
   cp .env.example .env
   # Edit .env with your Azure AI Foundry credentials
   ```

5. **For deployment, configure azd environment**:
   ```bash
   azd auth login
   azd env new <environment-name>
   azd env set AZURE_OPENAI_ENDPOINT <your-ai-foundry-endpoint>
   azd env set AZURE_OPENAI_API_KEY <your-ai-foundry-api-key>
   ```

6. **Deploy to Azure** (optional):
   ```bash
   azd up
   ```

### Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
./start.sh

# Frontend (in a new terminal)
cd frontend
npm install
npm start
```

The application will be available at `http://127.0.0.1:5173`.

## GitHub Actions Deployment

### Azure Service Principal Setup

Before setting up GitHub Actions deployment, you need to create an Azure Service Principal with appropriate permissions.

#### Step 1: Create Azure Service Principal

You can create a service principal using either the Azure CLI or Azure Portal.

##### Using Azure CLI (Recommended)

1. **Install Azure CLI** if you haven't already:
   ```bash
   # Install Azure CLI (see: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?WT.mc_id=AI-MVP-5004204)
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Get your subscription ID**:
   ```bash
   az account show --query id --output tsv
   ```

4. **Create a service principal**:
   ```bash
   # Replace <subscription-id> with your actual subscription ID
   az ad sp create-for-rbac --name "str-agentic-adventures-deploy" \
     --role "Contributor" \
     --scopes "/subscriptions/<subscription-id>" \
     --json-auth
   ```

   This command will output JSON similar to:
   ```json
   {
     "clientId": "12345678-1234-1234-1234-123456789012",
     "clientSecret": "your-client-secret",
     "subscriptionId": "87654321-4321-4321-4321-210987654321",
     "tenantId": "11111111-1111-1111-1111-111111111111",
     "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
     "resourceManagerEndpointUrl": "https://management.azure.com/",
     "activeDirectoryGraphResourceId": "https://graph.windows.net/",
     "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
     "galleryEndpointUrl": "https://gallery.azure.com/",
     "managementEndpointUrl": "https://management.core.windows.net/"
   }
   ```

   **Save this output** - you'll need these values for GitHub secrets.

##### Using Azure Portal

1. Go to **Azure Active Directory** > **App registrations** > **New registration**
2. Name: `str-agentic-adventures-deploy`
3. Supported account types: **Accounts in this organizational directory only**
4. Click **Register**
5. Note the **Application (client) ID** and **Directory (tenant) ID**
6. Go to **Certificates & secrets** > **New client secret**
7. Add description and expiration, click **Add**
8. **Copy the secret value immediately** (it won't be shown again)
9. Go to **Subscriptions** > Select your subscription > **Access control (IAM)**
10. Click **Add** > **Add role assignment**
11. Role: **Contributor**
12. Assign access to: **User, group, or service principal**
13. Search for your app registration name and assign

#### Step 2: Configure Authentication Method

Choose one of the following authentication methods:

##### Option 1: Federated Credentials (Recommended - No Secrets!)

This method uses OpenID Connect and doesn't require storing client secrets.

1. **In Azure Portal**, go to your App Registration > **Certificates & secrets** > **Federated credentials**

2. **Add credential** with these settings:
   - Federated credential scenario: **GitHub Actions deploying Azure resources**
   - Organization: `your-github-username` (or organization name)
   - Repository: `str-agentic-adventures`
   - Entity type: **Branch**
   - GitHub branch name: `main`
   - Name: `main-branch-deploy`

3. **Add another credential** for pull requests:
   - Same settings as above, but:
   - Entity type: **Pull request**
   - Name: `pull-request-deploy`

4. **Required GitHub Secrets** (Go to your GitHub repository > Settings > Secrets and variables > Actions):
   - `AZURE_CLIENT_ID`: The Application (client) ID from your service principal
   - `AZURE_TENANT_ID`: The Directory (tenant) ID from your service principal
   - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
   - `AZURE_OPENAI_ENDPOINT`: Your Azure AI Foundry endpoint URL (e.g., `https://your-project.openai.azure.com/`)
   - `AZURE_OPENAI_API_KEY`: Your Azure AI Foundry API key

##### Option 2: Service Principal with Client Secret

If you prefer using client secrets or federated credentials aren't available:

1. **Use the client secret** created during service principal setup

2. **Required GitHub Secrets**:
   - `AZURE_CREDENTIALS`: The complete JSON output from the `az ad sp create-for-rbac` command
   - `AZURE_OPENAI_ENDPOINT`: Your Azure AI Foundry endpoint URL
   - `AZURE_OPENAI_API_KEY`: Your Azure AI Foundry API key

#### Step 3: Obtain Azure AI Foundry Information

1. **In Azure AI Foundry**, go to [ai.azure.com](https://ai.azure.com) and select your project
2. **Endpoint**: Found in **Project settings** (e.g., `https://your-project.openai.azure.com/`)
3. **API Key**: In **Project settings** > **Keys and Endpoint**, copy one of the available keys
4. **Model Deployments**: Go to **Deployments** to verify your deployed models (gpt-4o-mini, text-embedding-ada-002, dall-e-3)

> **Note**: Azure AI Foundry provides a unified interface for managing your Azure OpenAI resources. If you prefer using the Azure Portal directly, you can access your Azure OpenAI Service resource, but Azure AI Foundry is the recommended approach.

### GitHub Repository Configuration

#### Required Secrets
Configure these in your GitHub repository (Settings > Secrets and variables > Actions > Repository secrets):

**For Federated Credentials:**
- `AZURE_CLIENT_ID`: Application (client) ID from service principal
- `AZURE_TENANT_ID`: Directory (tenant) ID from service principal
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_OPENAI_ENDPOINT`: Azure AI Foundry endpoint URL (from Project settings)
- `AZURE_OPENAI_API_KEY`: Azure AI Foundry API key (from Project settings)

**For Service Principal with Secret:**
- `AZURE_CREDENTIALS`: Complete JSON from service principal creation
- `AZURE_OPENAI_ENDPOINT`: Azure AI Foundry endpoint URL (from Project settings)
- `AZURE_OPENAI_API_KEY`: Azure AI Foundry API key (from Project settings)

#### Optional Repository Variables
Configure these in Settings > Secrets and variables > Actions > Repository variables:

- `AZURE_LOCATION`: Azure region (default: eastus)
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Chat model deployment name (default: gpt-4o-mini)
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Embedding model deployment name (default: text-embedding-ada-002)
- `AZURE_OPENAI_DALLE_DEPLOYMENT`: DALL-E deployment name (default: dall-e-3)

#### Finding Your Azure Values

**Subscription ID:**
```bash
az account show --query id --output tsv
```

**Tenant ID:**
```bash
az account show --query tenantId --output tsv
```

#### Finding Your Azure Values

**Subscription ID:**
```bash
az account show --query id --output tsv
```

**Tenant ID:**
```bash
az account show --query tenantId --output tsv
```

**Or in Azure Portal:** Go to **Azure Active Directory** > **Overview** to find your Tenant ID

### Verification and Testing

#### Test Your Service Principal Setup

Before running GitHub Actions, verify your service principal works:

1. **Test Azure CLI login with service principal**:
   ```bash
   # For federated credentials (this won't work locally, but tests the SP exists)
   az login --service-principal \
     --username "<AZURE_CLIENT_ID>" \
     --tenant "<AZURE_TENANT_ID>" \
     --federated-token "dummy"  # This will fail but shows if SP exists

   # For client secret method
   az login --service-principal \
     --username "<AZURE_CLIENT_ID>" \
     --password "<CLIENT_SECRET>" \
     --tenant "<AZURE_TENANT_ID>"
   ```

2. **Test permissions**:
   ```bash
   # List resource groups (should work if permissions are correct)
   az group list --query "[].name" --output tsv

   # Test creating a resource group (then delete it)
   az group create --name "test-permissions-rg" --location "eastus"
   az group delete --name "test-permissions-rg" --yes --no-wait
   ```

3. **Test Azure AI Foundry / Azure OpenAI access**:
   ```bash
   # Test if you can access your Azure AI Foundry endpoint
   curl -H "api-key: <YOUR_AI_FOUNDRY_API_KEY>" \
        "<YOUR_AI_FOUNDRY_ENDPOINT>/openai/deployments?api-version=2023-03-15-preview"
   ```

#### Validate GitHub Actions Setup

1. **Check secrets are configured**: Go to your repository > Settings > Secrets and variables > Actions
2. **Run a manual deployment**: Go to Actions > "Deploy to Production" > "Run workflow"
3. **Check workflow logs**: If the deployment fails, review the GitHub Actions logs for specific error messages

### Deployment Workflows

> **Note**: When a workflow triggers on `pull_request` with `branches: [ main ]`, it runs when pull requests are opened/updated that **target** the main branch, not when pushing **to** the main branch. This allows testing changes before they are merged.

#### Production Deployment
- **Trigger**: Push to `main` branch or manual trigger
- **Workflow**: `.github/workflows/deploy-production.yml`
- **Environment**: production
- **Resources**: Creates a production environment with all Azure resources

#### Pull Request Environments
- **Trigger**: Pull request opened/updated against `main` branch (runs when PRs target main, not when pushing to main)
- **Workflow**: `.github/workflows/deploy-pr.yml`
- **Environment**: development (temporary environment named `pr-{PR_NUMBER}`)
- **Resources**: Creates a temporary environment for testing each pull request
- **Purpose**: Allows testing changes in isolation before merging to main

#### Environment Cleanup
- **Trigger**: Pull request closed/merged (automatically cleans up when PR is finished)
- **Workflow**: `.github/workflows/cleanup-pr.yml`
- **Action**: Deletes the temporary PR environment (`pr-{PR_NUMBER}`)
- **Purpose**: Ensures no orphaned environments remain after PR completion

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
- Uses your existing **Azure AI Foundry project** for AI capabilities (Azure OpenAI models)

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
- Shared Azure AI Foundry project to minimize AI costs

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

#### Authentication Issues
1. **"Failed to authenticate"**:
   - Verify your service principal credentials are correct
   - Check that federated credentials are configured for the correct GitHub repository and branch
   - Ensure the service principal has not expired (client secrets expire)

2. **"Insufficient privileges"**:
   - Verify the service principal has **Contributor** role on the subscription
   - Check that the service principal is assigned to the correct subscription
   - Ensure the role assignment hasn't expired

3. **"Invalid client secret"**:
   - Client secrets expire - create a new one in Azure Portal
   - Verify the secret is copied correctly to GitHub secrets
   - Check there are no extra spaces or characters in the secret

#### Resource and Access Issues
4. **Azure AI Foundry / Azure OpenAI Access**:
   - Ensure your subscription has access to Azure OpenAI service through Azure AI Foundry
   - Verify your Azure AI Foundry project is in the same subscription as your deployment
   - Check that the Azure AI Foundry endpoint URL and API key are correct
   - Confirm your model deployments are active in Azure AI Foundry

5. **Resource Limits**:
   - Check subscription limits for Container Apps and Static Web Apps
   - Verify quota availability in your chosen Azure region
   - Consider using a different region if capacity is limited

6. **Deployment Failures**:
   - Check that resource names don't conflict with existing resources
   - Verify all required Azure providers are registered in your subscription
   - Review Azure Activity Log for detailed error messages

## API Endpoint Structure

### Development Environment

When running locally, the backend serves API endpoints directly without a prefix:

**HTTP API Endpoints:**
- Base URL: `http://localhost:8000`
- Game routes: `/game/*` (e.g., `/game/campaign`, `/game/character`, `/game/input`)
- Health check: `/health`
- Root: `/`

**WebSocket Endpoints:**
- Base URL: `ws://localhost:8000`
- Chat WebSocket: `/ws/chat/{campaign_id}`
- Legacy WebSocket: `/ws/{campaign_id}`

**Example URLs:**
```
http://localhost:8000/health
http://localhost:8000/game/campaign/templates
http://localhost:8000/game/character
http://localhost:8000/game/input
ws://localhost:8000/ws/chat/12345
```

### Production Deployment with Reverse Proxy

When deploying behind a reverse proxy (e.g., Azure Application Gateway, nginx), the backend application should still expose endpoints at the root level as shown above. The reverse proxy configuration should handle URL routing:

**Reverse Proxy Configuration Example (nginx):**
```nginx
# Route /api/* requests to backend at /game/*
location /api/game/ {
    proxy_pass http://backend:8000/game/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Route /ws/* WebSocket requests to backend /ws/*
location /ws/ {
    proxy_pass http://backend:8000/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**Important Notes:**
1. **Backend Configuration**: The FastAPI application does NOT use `root_path="/api"` - it serves routes at the root level
2. **Reverse Proxy Responsibility**: The reverse proxy (Azure Application Gateway, nginx, etc.) handles `/api` prefix routing
3. **Frontend Configuration**: The frontend should be configured to use `/api` prefix in production via environment variables
4. **WebSocket Handling**: WebSocket connections require special proxy configuration to handle the `Upgrade` header

### Frontend Configuration

The frontend uses environment-based URL configuration:

**Development (`src/utils/urls.ts`):**
```typescript
export const getApiBaseUrl = (): string => {
  return "http://localhost:8000";  // No /api prefix
};

export const getWebSocketBaseUrl = (): string => {
  return "ws://localhost:8000";  // No /api prefix
};
```

**Production:** Configure frontend build with environment variables to use `/api` prefix when deployed behind reverse proxy.

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