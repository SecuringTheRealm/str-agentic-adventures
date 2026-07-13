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
param deployImageModel bool = true

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

// gpt-5-mini — default/general chat model: combat, cartographer and narrator
// agents use this tier unless overridden via their own deployment env var.
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-5-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5-mini'
      version: '2025-08-07'
    }
  }
}

// gpt-5 — premium reasoning tier for the Dungeon Master orchestrator agent.
// A 'Hosted on Azure' (v2) Claude deployment (e.g. claude-sonnet-5) is an
// equally valid DM/Narrator brain — point AZURE_OPENAI_DM_DEPLOYMENT /
// AZURE_OPENAI_NARRATOR_DEPLOYMENT at it via env var once deployed. Do not
// add Marketplace/CCU Claude deployments here.
resource dmDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-5'
  sku: {
    name: 'GlobalStandard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5'
      version: '2025-08-07'
    }
  }
  dependsOn: [chatDeployment]
}

// gpt-5-nano — cheapest tier for the Scribe (note-taking) and Artist
// (image-prompt drafting) agents.
resource nanoDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-5-nano'
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5-nano'
      version: '2025-08-07'
    }
  }
  dependsOn: [dmDeployment]
}

// gpt-realtime-mini — real-time voice for DM narration via WebRTC
resource realtimeDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-realtime-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-realtime-mini'
      version: '2025-12-15'
    }
  }
  dependsOn: [nanoDeployment]
}

// gpt-image-1-mini — cost-efficient image generation for the Artist agent.
// Set deployImageModel=false if this subscription hasn't been granted
// access to the (limited-access preview) image model.
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
  dependsOn: [realtimeDeployment]
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

@description('The default project endpoint (AIServices kind accounts get an implicit default project named after the account)')
output projectEndpoint string = 'https://${foundry.name}.services.ai.azure.com/api/projects/${foundry.name}'

@description('The resource name')
output name string = foundry.name

@description('The resource ID')
output id string = foundry.id

@description('Default/general chat deployment name (gpt-5-mini)')
output chatDeploymentName string = chatDeployment.name

@description('Premium reasoning deployment name for the DM agent (gpt-5)')
output dmDeploymentName string = dmDeployment.name

@description('Cheapest-tier deployment name for Scribe/Artist agents (gpt-5-nano)')
output nanoDeploymentName string = nanoDeployment.name

@description('Realtime voice deployment name (gpt-realtime-mini)')
output realtimeDeploymentName string = realtimeDeployment.name

@description('Image generation deployment name, empty string if not deployed')
output imageDeploymentName string = deployImageModel ? imageDeployment.name : ''

// API key intentionally not output — use managed identity auth in all environments
