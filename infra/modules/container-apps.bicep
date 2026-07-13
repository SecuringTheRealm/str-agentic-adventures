@description('Name of the Container App')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

@description('Resource ID of the Container Apps managed environment')
param containerAppsEnvironmentId string

@description('Login server of the container registry (e.g. myacr.azurecr.io)')
param containerRegistryLoginServer string

@description('Resource ID of the user-assigned managed identity')
param managedIdentityId string

@description('Client ID of the user-assigned managed identity (DefaultAzureCredential needs this to pick the right identity)')
param managedIdentityClientId string

@description('Container image to deploy. azd overwrites this with the built backend image on `azd deploy`; a placeholder is used on first provision.')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Port the backend listens on')
param targetPort int = 8000

@description('Key Vault URI (with trailing slash) used to build Key Vault secret references')
param keyVaultUri string

@description('Azure AI Foundry / Azure OpenAI endpoint')
param azureOpenAiEndpoint string

@description('Azure AI Foundry project endpoint')
param azureAiProjectEndpoint string

@description('General/default chat model deployment name')
param chatDeployment string

@description('Dungeon Master agent model deployment name')
param dmDeployment string

@description('Narrator agent model deployment name')
param narratorDeployment string

@description('Combat MC agent model deployment name')
param combatDeployment string

@description('Combat Cartographer agent model deployment name')
param cartographerDeployment string

@description('Scribe agent model deployment name')
param scribeDeployment string

@description('Artist agent model deployment name')
param artistDeployment string

@description('Image generation deployment name (empty string if not deployed)')
param imageDeployment string

@description('Realtime voice deployment name')
param realtimeDeployment string

@description('Storage account name (blob access uses managed identity, not a connection string)')
param storageAccountName string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('PostgreSQL server host')
param databaseHost string

@description('PostgreSQL database name')
param databaseName string

@description('PostgreSQL administrator login')
param databaseUser string

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'backend' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId
        }
      ]
      // Secrets are pulled directly from Key Vault via the managed identity —
      // no plaintext secret values live in this template or in the Container
      // App's configuration (#744).
      secrets: [
        {
          name: 'database-password'
          keyVaultUrl: '${keyVaultUri}secrets/database-password'
          identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: containerImage
          resources: {
            cpu: json('1.0')
            memory: '2.0Gi'
          }
          env: [
            { name: 'AZURE_CLIENT_ID', value: managedIdentityClientId }
            { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAiEndpoint }
            { name: 'AZURE_AI_PROJECT_ENDPOINT', value: azureAiProjectEndpoint }
            { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: chatDeployment }
            { name: 'AZURE_OPENAI_DM_DEPLOYMENT', value: dmDeployment }
            { name: 'AZURE_OPENAI_NARRATOR_DEPLOYMENT', value: narratorDeployment }
            { name: 'AZURE_OPENAI_COMBAT_DEPLOYMENT', value: combatDeployment }
            { name: 'AZURE_OPENAI_CARTOGRAPHER_DEPLOYMENT', value: cartographerDeployment }
            { name: 'AZURE_OPENAI_SCRIBE_DEPLOYMENT', value: scribeDeployment }
            { name: 'AZURE_OPENAI_ARTIST_DEPLOYMENT', value: artistDeployment }
            { name: 'AZURE_OPENAI_IMAGE_DEPLOYMENT', value: imageDeployment }
            { name: 'AZURE_OPENAI_REALTIME_DEPLOYMENT', value: realtimeDeployment }
            { name: 'AZURE_STORAGE_ACCOUNT_NAME', value: storageAccountName }
            { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
            { name: 'DATABASE_HOST', value: databaseHost }
            { name: 'DATABASE_NAME', value: databaseName }
            { name: 'DATABASE_USER', value: databaseUser }
            { name: 'DATABASE_PASSWORD', secretRef: 'database-password' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

@description('Resource ID of the Container App')
output id string = containerApp.id

@description('Name of the Container App')
output name string = containerApp.name

@description('Fully qualified domain name of the Container App ingress')
output fqdn string = containerApp.properties.configuration.ingress.fqdn
