@description('Name of the AI Foundry resource')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

@description('Whether to disable local (key-based) auth')
param disableLocalAuth bool = false

@description('Principal ID of the managed identity to grant Cognitive Services OpenAI User role')
param managedIdentityPrincipalId string

@description('Deploy image generation model (requires gated access on some subscriptions)')
param deployImageModel bool = false

@description('Deploy non-OpenAI models (Phi, Llama — may require Marketplace agreement)')
param deployPartnerModels bool = false

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    customSubDomainName: name
    disableLocalAuth: disableLocalAuth
    publicNetworkAccess: 'Enabled'
  }
}

// GPT-4.1-mini — primary chat model (replaces retiring gpt-4o-mini)
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-41-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 8
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4.1-mini'
      version: '2025-04-14'
    }
  }
}

// text-embedding-3-small — cheaper and better than ada-002
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'text-embedding-3-small'
  sku: {
    name: 'GlobalStandard'
    capacity: 8
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
  }
  dependsOn: [chatDeployment]
}

// Image generation — disabled by default (all models are gated or deprecated on this subscription)
// Enable with deployImageModel=true once gpt-image-1-mini access is granted
resource imageDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = if (deployImageModel) {
  parent: foundry
  name: 'gpt-image-1-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-image-1-mini'
      version: '2025-10-06'
    }
  }
  dependsOn: [embeddingDeployment]
}

// Phi-4-mini — cheap reasoning for rules lookups and simple decisions
resource phiDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = if (deployPartnerModels) {
  parent: foundry
  name: 'Phi-4-mini-instruct'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'Microsoft'
      name: 'Phi-4-mini-instruct'
    }
  }
  dependsOn: [embeddingDeployment]
}

// Llama-4-Scout — open-weight storytelling for lore generation
resource llamaDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = if (deployPartnerModels) {
  parent: foundry
  name: 'Llama-4-Scout-17B-16E-Instruct'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'Meta'
      name: 'Llama-4-Scout-17B-16E-Instruct'
    }
  }
  dependsOn: [phiDeployment]
}

// Cognitive Services OpenAI User role for the managed identity
resource openAiUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundry.id, managedIdentityPrincipalId, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  scope: foundry
  properties: {
    // Cognitive Services OpenAI User
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('The endpoint URL for the AI Foundry resource')
output endpoint string = foundry.properties.endpoint

@description('The resource name')
output name string = foundry.name

@description('The resource ID')
output id string = foundry.id

// API key intentionally not output — use managed identity auth in all environments
