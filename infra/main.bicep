// main.bicep
param location string
param postgresAdminUser string
@secure()
param postgresAdminPassword string
param postgresDbName string = 'ai_app'
param acrName string = '${uniqueString(resourceGroup().id)}acr'

// Resource: Azure Container Registry (ACR)
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// Resource: Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Resource: Container Apps Environment
resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${resourceGroup().name}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Resource: PostgreSQL Flexible Server
resource pgServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: uniqueString(resourceGroup().id, 'pg')
  location: location
  properties: {
    version: '16'
    administratorLogin: 'postgresql_user'
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 32
    }
    createMode: 'Create'
    availabilityZone: '1'
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
  sku: {
    name: 'Standard_B2s'
    tier: 'Burstable'
  }
}

// Resource: Initial Database
resource pgDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  name: postgresDbName
  parent: pgServer
  properties: {
    charset: 'UTF8'
    collation: 'en_US.UTF8'
  }
}

// Resource: Firewall rule to allow Azure services
resource pgAllowAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  name: 'AllowAllAzureServices'
  parent: pgServer
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Resource: API Container App
resource apiContainerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ai-starter-api'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 4000
        allowInsecure: false
        transport: 'auto'
        corsPolicy: {
          allowedOrigins: ['*']
        }
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: 'system'
        }
      ]
      secrets: [
        {
          name: 'database-url'
          value: 'postgres://postgresql_user:${postgresAdminPassword}@${pgServer.name}.postgres.database.azure.com:5432/${postgresDbName}?sslmode=require'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${acr.properties.loginServer}/api:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'PORT'
              value: '4000'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

// Resource: Role Assignment for ACR Pull
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, apiContainerApp.name, 'acrpull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: apiContainerApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Resource: Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2022-03-01' = {
  name: 'ai-starter-web'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
}

// Outputs
output API_URL string = apiContainerApp.properties.configuration.ingress.fqdn
output STATIC_WEB_APP_URL string = staticWebApp.properties.defaultHostname
