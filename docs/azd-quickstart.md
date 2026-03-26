# Azure Developer CLI Quick Start

This guide covers deploying Secure the Realm using [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview?WT.mc_id=AI-MVP-5004204).

## Prerequisites

- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd?WT.mc_id=AI-MVP-5004204) v1.5+
- An Azure subscription with permissions to create resources
- Docker (for building the backend container image)

## One-command deploy

```bash
azd up
```

This provisions all infrastructure (Container Apps, Static Web App, PostgreSQL, Key Vault, Storage, Application Insights) and deploys both the backend and frontend.

On first run, `azd` will prompt you for:
- **Environment name** -- used as a prefix for all Azure resources
- **Azure location** -- the region to deploy to (e.g. `uksouth`)
- **Azure subscription** -- which subscription to bill

## Post-deploy configuration

After `azd up` completes, set the Azure OpenAI configuration:

```bash
azd env set AZURE_OPENAI_ENDPOINT https://your-openai-resource.openai.azure.com/
azd env set AZURE_OPENAI_CHAT_DEPLOYMENT gpt-4o-mini
azd env set AZURE_OPENAI_EMBEDDING_DEPLOYMENT text-embedding-ada-002
azd env set AZURE_OPENAI_DALLE_DEPLOYMENT gpt-image-1-mini
```

Then redeploy to pick up the new values:

```bash
azd deploy
```

## Environment management

```bash
# Create a dev environment
azd env new dev
azd env set AZURE_LOCATION uksouth

# Create a prod environment
azd env new prod
azd env set AZURE_LOCATION uksouth

# Switch between environments
azd env select dev

# View current environment values
azd env get-values

# List all environments
azd env list
```

## Common commands

| Command | Description |
|---|---|
| `azd up` | Provision infrastructure and deploy code |
| `azd provision` | Provision infrastructure only (no code deploy) |
| `azd deploy` | Deploy code only (infrastructure must exist) |
| `azd down` | Tear down all provisioned resources |
| `azd monitor --overview` | Open the Application Insights dashboard |
| `azd monitor --live` | Open live metrics stream |
| `azd env get-values` | Show all environment variable values |

## Pipeline setup (GitHub Actions with OIDC)

```bash
azd pipeline config
```

This configures federated credentials for GitHub Actions using OpenID Connect -- no service principal secrets needed. It creates:
- An Azure AD app registration
- Federated identity credentials for your GitHub repository
- GitHub repository secrets (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`)

See the [azd pipeline documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/configure-devops-pipeline?WT.mc_id=AI-MVP-5004204) for details.

## Architecture

`azd` uses the following project structure:

```
azure.yaml              # Service definitions and hooks
infra/
  main.bicep            # Infrastructure-as-code (subscription-scoped)
  main.bicepparam       # Default parameter values
  modules/              # Reusable Bicep modules
  parameters/
    dev.bicepparam      # Development environment defaults
    prod.bicepparam     # Production environment defaults
```

The infrastructure provisions:
- **Container Apps** environment with the backend API
- **Static Web App** for the frontend
- **PostgreSQL Flexible Server** for persistent storage
- **Azure Key Vault** for secrets
- **Azure Storage** for blob/file storage
- **Container Registry** for Docker images
- **Application Insights** + Log Analytics for observability
- **Managed Identity** for passwordless Azure service authentication
- **Cost budget** with alert notifications

## Troubleshooting

**`azd up` fails during provisioning**
Check that your subscription has quota for the resources in the target region. Run `azd provision` separately with `--debug` for detailed logs.

**Frontend shows API errors after deploy**
The frontend build embeds the backend URL at build time. Run `azd deploy` again after the backend is healthy.

**Switching environments**
The `.azure/` directory stores local environment config (including secrets) and is gitignored. Each developer manages their own environments locally.
