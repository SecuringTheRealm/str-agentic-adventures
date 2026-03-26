@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@minLength(1)
@maxLength(90)
@description('Name of the resource group to create or use')
param resourceGroupName string = '${environmentName}-rg'

@description('Azure OpenAI API Key (optional — managed identity is preferred)')
@secure()
param azureOpenAiApiKey string = ''

@description('Azure OpenAI Endpoint')
param azureOpenAiEndpoint string = ''

@description('Azure OpenAI Chat Deployment Name')
param azureOpenAiChatDeployment string = 'gpt-4o-mini'

@description('Azure OpenAI Embedding Deployment Name')
param azureOpenAiEmbeddingDeployment string = 'text-embedding-ada-002'

@description('Azure OpenAI Image Generation Deployment Name')
param azureOpenAiDalleDeployment string = 'gpt-image-1-mini'

@secure()
@description('Administrator password for the PostgreSQL server (auto-generated if not provided)')
param databasePassword string = newGuid()

// This template should be deployed at the subscription level to create the resource group
targetScope = 'subscription'

// Generate a unique suffix based on the environment name and subscription
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// Create Log Analytics workspace for monitoring
module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'log-analytics'
  scope: rg
  params: {
    name: '${environmentName}-logs-${resourceToken}'
    location: location
    tags: tags
  }
}

// Create Container Apps environment
module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: '${environmentName}-cae-${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Create Storage Account for file storage
module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: 'st${resourceToken}'
    location: location
    tags: tags
  }
}

// Create Azure Container Registry for backend images
module containerRegistry 'modules/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: 'acr${resourceToken}'
    location: location
    tags: tags
  }
}

// Create User-Assigned Managed Identity for container app
module managedIdentity 'modules/managed-identity.bicep' = {
  name: 'managed-identity'
  scope: rg
  params: {
    name: '${environmentName}-id-${resourceToken}'
    location: location
    tags: tags
  }
}

// Create Key Vault for secret storage
module keyVault 'modules/key-vault.bicep' = {
  name: 'key-vault'
  scope: rg
  params: {
    name: '${environmentName}-kv-${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
  }
}

// Create PostgreSQL Flexible Server for persistent database storage
module postgresql 'modules/postgresql.bicep' = {
  name: 'postgresql'
  scope: rg
  params: {
    name: '${environmentName}-pg-${resourceToken}'
    location: location
    tags: tags
    administratorLoginPassword: databasePassword
    keyVaultName: keyVault.outputs.name
  }
}

// Assign roles to managed identity (AcrPull + Storage Blob Data Contributor)
module roleAssignments 'modules/role-assignments.bicep' = {
  name: 'role-assignments'
  scope: rg
  params: {
    principalId: managedIdentity.outputs.principalId
    acrName: containerRegistry.outputs.name
    storageAccountName: storage.outputs.name
  }
}

// Backend Container App will be deployed separately via GitHub Actions workflow
// This ensures the latest code is always deployed without requiring Bicep updates

// Create Frontend Static Web App
module frontend 'modules/frontend.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: '${environmentName}-frontend-${resourceToken}'
    location: location
    tags: tags
    backendUrl: 'https://production-backend.${containerAppsEnvironment.outputs.defaultDomain}/api'
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId

output FRONTEND_URI string = frontend.outputs.uri

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.outputs.id
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name
output AZURE_STATIC_WEB_APP_NAME string = frontend.outputs.name
output AZURE_MANAGED_IDENTITY_ID string = managedIdentity.outputs.id
output AZURE_MANAGED_IDENTITY_CLIENT_ID string = managedIdentity.outputs.clientId
output AZURE_MANAGED_IDENTITY_PRINCIPAL_ID string = managedIdentity.outputs.principalId
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output DATABASE_HOST string = postgresql.outputs.host
output DATABASE_NAME string = postgresql.outputs.databaseName