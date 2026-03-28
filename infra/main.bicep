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

@secure()
@description('Administrator password for the PostgreSQL server (auto-generated if not provided)')
param databasePassword string = newGuid()

@description('Monthly cost budget amount in billing currency')
param budgetAmount int = 50

@description('Email addresses for cost budget alert notifications')
param budgetContactEmails array = []

@description('Budget start date in yyyy-MM-ddT00:00:00Z format. Defaults to the first of the current month.')
param budgetStartDate string = '${utcNow('yyyy-MM')}-01T00:00:00Z'

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

// Create Application Insights for observability
module appInsights 'modules/application-insights.bicep' = {
  name: 'application-insights'
  scope: rg
  params: {
    name: '${environmentName}-ai-${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
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

// Create Azure AI Foundry resource with model deployments
module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'ai-foundry'
  scope: rg
  params: {
    name: '${environmentName}-foundry-${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
  }
}

// Backend Container App will be deployed separately via GitHub Actions workflow
// This ensures the latest code is always deployed without requiring Bicep updates

// Create cost budget with alert notifications (only if contact emails provided)
module budget 'modules/budget.bicep' = if (length(budgetContactEmails) > 0) {
  name: 'budget'
  scope: rg
  params: {
    name: '${environmentName}-monthly-budget'
    amount: budgetAmount
    contactEmails: budgetContactEmails
    startDate: budgetStartDate
  }
}

// Create Frontend Static Web App
module frontend 'modules/frontend.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: '${environmentName}-frontend-${resourceToken}'
    location: 'westeurope'  // Static Web Apps not available in all regions; westeurope is nearest supported
    tags: tags
    backendUrl: 'https://${environmentName}-backend.${containerAppsEnvironment.outputs.defaultDomain}/api'
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
output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString
output AZURE_OPENAI_ENDPOINT string = aiFoundry.outputs.endpoint
output AZURE_AI_FOUNDRY_NAME string = aiFoundry.outputs.name