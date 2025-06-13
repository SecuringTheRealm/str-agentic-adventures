@description('The name of the Container App')
param name string

@description('The location of the Container App')
param location string

@description('Tags to apply to the Container App')
param tags object = {}

@description('The resource ID of the Container Apps environment')
param containerAppsEnvironmentId string

@description('Azure OpenAI API Key')
@secure()
param azureOpenAiApiKey string

@description('Azure OpenAI Endpoint')
param azureOpenAiEndpoint string

@description('Azure OpenAI Chat Deployment Name')
param azureOpenAiChatDeployment string

@description('Azure OpenAI Embedding Deployment Name')
param azureOpenAiEmbeddingDeployment string

@description('Azure OpenAI DALL-E Deployment Name')
param azureOpenAiDalleDeployment string

@description('Storage account name to retrieve connection string from')
param storageAccountName string

@description('Storage account resource group (defaults to current resource group)')
param storageAccountResourceGroup string = resourceGroup().name

// Reference existing storage account to retrieve connection string securely
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
  scope: resourceGroup(storageAccountResourceGroup)
}

resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      secrets: [
        {
          name: 'azure-openai-api-key'
          value: azureOpenAiApiKey
        }
        {
          name: 'storage-connection-string'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
        }
      ]
    }
    template: {
      containers: [
        {
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          name: 'backend'
          env: [
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2023-12-01-preview'
            }
            {
              name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
              value: azureOpenAiChatDeployment
            }
            {
              name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
              value: azureOpenAiEmbeddingDeployment
            }
            {
              name: 'AZURE_OPENAI_DALLE_DEPLOYMENT'
              value: azureOpenAiDalleDeployment
            }
            {
              name: 'STORAGE_CONNECTION_STRING'
              secretRef: 'storage-connection-string'
            }
            {
              name: 'APP_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'APP_PORT'
              value: '8000'
            }
            {
              name: 'APP_DEBUG'
              value: 'false'
            }
            {
              name: 'APP_LOG_LEVEL'
              value: 'info'
            }
            {
              name: 'SEMANTIC_KERNEL_DEBUG'
              value: 'false'
            }
          ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output id string = backendApp.id
output name string = backendApp.name
output uri string = 'https://${backendApp.properties.configuration.ingress.fqdn}'