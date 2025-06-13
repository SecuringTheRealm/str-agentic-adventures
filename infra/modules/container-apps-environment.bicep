@description('The name of the Container Apps environment')
param name string

@description('The location of the Container Apps environment')
param location string

@description('Tags to apply to the Container Apps environment')
param tags object = {}

@description('The resource ID of the Log Analytics workspace')
param logAnalyticsWorkspaceId string

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2022-10-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2022-10-01').primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

output id string = containerAppsEnvironment.id
output name string = containerAppsEnvironment.name
output defaultDomain string = containerAppsEnvironment.properties.defaultDomain