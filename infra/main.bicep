// main.bicep
param location string = resourceGroup().location
param acrName string = '${uniqueString(resourceGroup().id)}acr'
param postgresAdminUser string
@secure()
param postgresAdminPassword string
param postgresDbName string = 'ai_app'

// Resource: Azure Container Registry (ACR)
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// Resource: Container Apps Environment
resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${resourceGroup().name}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
    }
  }
}

// Resource: PostgreSQL Flexible Server
resource pgServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: uniqueString(resourceGroup().id, 'pg')
  location: location
  properties: {
    version: '16'
    administratorLogin: postgresAdminUser
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
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
  sku: {
    name: 'Standard_B1ms'
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
  name: '${azdEnvironment().environmentName}-api'
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 4000
        allowInsecure: false
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
          name: 'DATABASE_URL'
          value: 'postgres://${postgresAdminUser}:${postgresAdminPassword}@${pgServer.name}.postgres.database.azure.com:5432/${postgresDbName}?sslmode=require'
        }
      ]
    }
    identity: {
      type: 'SystemAssigned'
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${acr.properties.loginServer}/api:latest'
          resources: {
            cpu: 0.5
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'DATABASE_URL'
            },
            {
              name: 'PORT'
              value: '4000'
            }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 1 }
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
  name: '${azdEnvironment().environmentName}-web'
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
output API_URL string = 'https://${apiContainerApp.properties.configuration.ingress.fqdn}'
output STATIC_WEB_APP_URL string = 'https://${staticWebApp.properties.defaultHostname}'