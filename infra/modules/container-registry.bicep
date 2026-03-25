@description('The name of the container registry')
param name string

@description('The location of the container registry')
param location string

@description('Tags to apply to the container registry')
param tags object = {}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

output loginServer string = containerRegistry.properties.loginServer
output name string = containerRegistry.name
