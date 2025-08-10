@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Prefix for resource names')
param namePrefix string = 'str'

@description('PostgreSQL SKU name')
param postgresSkuName string = 'Standard_D2s_v5'

@description('PostgreSQL pricing tier')
param postgresTier string = 'GeneralPurpose'

@description('PostgreSQL version')
param postgresVersion string = '16'

@description('Database administrator login name (will be disabled in favor of AAD)')
param administratorLogin string = 'pgadmin'

@description('Database name')
param databaseName string = 'appdb'

// Virtual Network for private connectivity
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: '${namePrefix}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: ['10.20.0.0/16']
    }
    subnets: [
      {
        name: 'aca-infra'
        properties: {
          addressPrefix: '10.20.1.0/24'
          delegations: [
            {
              name: 'aca-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'aca-runtime'
        properties: {
          addressPrefix: '10.20.2.0/24'
          delegations: [
            {
              name: 'aca-runtime-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'db-subnet'
        properties: {
          addressPrefix: '10.20.3.0/24'
          delegations: [
            {
              name: 'pgflex-delegation'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
    ]
  }
}

// Private DNS Zone for PostgreSQL
resource pgPrivateDns 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${namePrefix}.postgres.database.azure.com'
  location: 'global'
  
  resource vnetLink 'virtualNetworkLinks@2020-06-01' = {
    name: 'vnetlink'
    location: 'global'
    properties: {
      virtualNetwork: {
        id: vnet.id
      }
      registrationEnabled: false
    }
  }
}

// PostgreSQL Flexible Server with AAD authentication
resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-11-01-preview' = {
  name: '${namePrefix}-pg'
  location: location
  sku: {
    name: postgresSkuName
    tier: postgresTier
  }
  properties: {
    version: postgresVersion
    administratorLogin: administratorLogin
    administratorLoginPassword: 'TempPassword123!' // Will be disabled
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled' // Only AAD authentication allowed
    }
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[2].id
      privateDnsZoneArmResourceId: pgPrivateDns.id
      publicNetworkAccess: 'Disabled'
    }
    storage: {
      storageSizeGB: 64
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled' // Can be enabled for production
    }
  }
}

// Database within the PostgreSQL server
resource db 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-12-01' = {
  name: databaseName
  parent: pg
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Container Apps Environment
resource acaEnv 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: '${namePrefix}-aca-env'
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: vnet.properties.subnets[0].id
      runtimeSubnetId: vnet.properties.subnets[1].id
    }
  }
}

// User-assigned managed identity for the backend container
resource backendUai 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: '${namePrefix}-backend-uami'
  location: location
}

// Backend Container App
resource backend 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-backend'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${backendUai.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: acaEnv.id
    configuration: {
      secrets: [] // No secrets needed with managed identity
      env: [
        {
          name: 'DATABASE_HOST'
          value: pg.properties.fullyQualifiedDomainName
        }
        {
          name: 'DATABASE_NAME'
          value: databaseName
        }
        {
          name: 'AZURE_POSTGRES_ENTRA_RESOURCE'
          value: 'https://ossrdbms-aad.database.windows.net/.default'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: backendUai.properties.clientId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: 'your-acr.azurecr.io/str-agentic-adventures:latest' // Update with actual ACR
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

// Outputs for other components
output postgresHost string = pg.properties.fullyQualifiedDomainName
output databaseName string = databaseName
output backendManagedIdentityId string = backendUai.id
output backendManagedIdentityClientId string = backendUai.properties.clientId
output vnetId string = vnet.id
output privateDnsZoneId string = pgPrivateDns.id