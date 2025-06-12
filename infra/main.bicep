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

@description('Azure OpenAI API Key')
@secure()
param azureOpenAiApiKey string = ''

@description('Azure OpenAI Endpoint')
param azureOpenAiEndpoint string = ''

@description('Azure OpenAI Chat Deployment Name')
param azureOpenAiChatDeployment string = 'gpt-4o-mini'

@description('Azure OpenAI Embedding Deployment Name')
param azureOpenAiEmbeddingDeployment string = 'text-embedding-ada-002'

@description('Azure OpenAI DALL-E Deployment Name')
param azureOpenAiDalleDeployment string = 'dall-e-3'

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

// Create Backend Container App
module backend 'modules/backend.bicep' = {
  name: 'backend'
  scope: rg
  params: {
    name: '${environmentName}-backend-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    azureOpenAiApiKey: azureOpenAiApiKey
    azureOpenAiEndpoint: azureOpenAiEndpoint
    azureOpenAiChatDeployment: azureOpenAiChatDeployment
    azureOpenAiEmbeddingDeployment: azureOpenAiEmbeddingDeployment
    azureOpenAiDalleDeployment: azureOpenAiDalleDeployment
    storageAccountName: storage.outputs.name
  }
}

// Create Frontend Static Web App
module frontend 'modules/frontend.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: '${environmentName}-frontend-${resourceToken}'
    location: location
    tags: tags
    backendUrl: backend.outputs.uri
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId

output BACKEND_URI string = backend.outputs.uri
output FRONTEND_URI string = frontend.outputs.uri

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.outputs.id
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name