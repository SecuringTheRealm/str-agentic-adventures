# Deployment Guide

This document explains how to deploy the STR Agentic Adventures application to Azure using the Azure Developer CLI (azd). It also covers the recommended local workflow built around the `uv` package manager.

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure AI Foundry Project**: You need access to Azure AI Foundry with the following models deployed:
   - gpt-41-mini for chat completion
   - gpt-realtime-mini for realtime voice (optional)
   - gpt-image-1-mini for image generation (optional)

> **Getting Started with Azure AI Foundry**: Visit [ai.azure.com](https://ai.azure.com) to create your project and deploy the required OpenAI models. Azure AI Foundry provides a unified platform for managing Azure OpenAI services and is the recommended way to access OpenAI models in Azure.

## Local Development Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 22+**
- **Azure CLI** (for authentication and deployment)
- **Azure AI Foundry project** with deployed models

### Step-by-Step Setup

1. **Install the Azure Developer CLI**:
   ```bash
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Clone this repository**:
   ```bash
   git clone https://github.com/SecuringTheRealm/str-agentic-adventures.git
   cd str-agentic-adventures
   ```

3. **Set up Azure AI Foundry credentials**:
   - Visit [Azure AI Foundry](https://ai.azure.com)
   - Create or select an existing project
   - Deploy required models (gpt-41-mini, gpt-realtime-mini, gpt-image-1-mini)
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
# Backend (from repository root)
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend (in a new terminal)
cd frontend
bun install
bun dev
```

The application will be available at `http://127.0.0.1:5173`.

## Production Deployment

Production deployment is manual via the Azure Developer CLI (azd) -- see [azd Quickstart](azd-quickstart.md) for the full walkthrough. There is no automated GitHub Actions production deployment workflow.

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

### Common Issues

#### Authentication Issues
1. **"Failed to authenticate" during `azd up`**:
   - Run `azd auth login` again
   - Verify your Azure account has Contributor access on the target subscription

#### Resource and Access Issues
2. **Azure AI Foundry / Azure OpenAI Access**:
   - Ensure your subscription has access to Azure OpenAI service through Azure AI Foundry
   - Verify your Azure AI Foundry project is in the same subscription as your deployment
   - Check that the Azure AI Foundry endpoint URL and API key are correct
   - Confirm your model deployments are active in Azure AI Foundry

3. **Resource Limits**:
   - Check subscription limits for Container Apps and Static Web Apps
   - Verify quota availability in your chosen Azure region
   - Consider using a different region if capacity is limited

4. **Deployment Failures**:
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

1. **Secrets Management**: All sensitive data stored as Azure Key Vault secrets or `azd` environment variables
2. **Network Security**: HTTPS enforced for all endpoints
3. **Authentication**: `DefaultAzureCredential` with minimal required RBAC role assignments
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
1. Run `azd up` with `--debug` for detailed error messages
2. Review Azure portal for resource status
3. Consult Azure Developer CLI documentation
4. Check Azure service health status
