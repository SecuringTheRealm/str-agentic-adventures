using 'main.bicep'

// These parameters will be overridden by the deployment workflows
param environmentName = 'default'
param location = 'eastus'
param resourceGroupName = 'default-rg'
param azureOpenAiEndpoint = ''
param azureOpenAiApiKey = ''
param azureOpenAiChatDeployment = 'gpt-4o-mini'
param azureOpenAiEmbeddingDeployment = 'text-embedding-ada-002'
param azureOpenAiDalleDeployment = 'dall-e-3'