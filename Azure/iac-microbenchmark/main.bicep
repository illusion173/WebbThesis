import {
  functionCombos
  linuxFXVersion
  runtimeMap
  keyvaultname
} from 'iac-inputs.bicep'

// param in cli call
param location string = resourceGroup().location
param tenantId string = subscription().tenantId
@description('Name of the Staging Slot')
param functionAppStagingSlot string = 'staging'

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'storageBenchWebbeecserau'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

var azStorageAccountPrimaryAccessKey = listkeys(storageAccount.id, storageAccount.apiVersion).keys[0].value

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'consumption-benchmark-plan-webb-eecserau'
  location: location
  sku: {
    name: 'Y1' // This is the Consumption Plan SKU
    tier: 'Dynamic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource appInsight 'Microsoft.Insights/components@2020-02-02' = {
  name: 'benchmarkAppInsight-webb-eecserau'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'FunctionApp'
    publicNetworkAccessForQuery: 'Enabled'
    publicNetworkAccessForIngestion: 'Enabled'
  }
}

// Reference the existing Key Vault, forces user to create the keys themselves, intentional
resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' existing = {
  name: keyvaultname // Replace with your existing Key Vault name
}

var InstrumentationKeyFromAppInsight = appInsight.properties.InstrumentationKey

resource functionApps 'Microsoft.Web/sites@2022-09-01' = [
  for i in range(0, length(functionCombos)): {
    name: '${functionCombos[i].full}-benchmark-app-webb-eecserau'
    location: location
    kind: 'functionapp,linux'
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      serverFarmId: appServicePlan.id
      siteConfig: {
        appSettings: [
          {
            name: 'AzureWebJobsStorage'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name}'
          }
          {
            name: 'FUNCTIONS_WORKER_RUNTIME'
            value: runtimeMap[functionCombos[i].language]
          }
          {
            name: 'FUNCTIONS_EXTENSION_VERSION'
            value: '~4'
          }
          {
            name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
            value: InstrumentationKeyFromAppInsight
          }
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: 'InstrumentationKey=${InstrumentationKeyFromAppInsight}'
          }
          {
            name: 'WEBSITE_CONTAINERSHARE'
            value: toLower(storageAccount.name)
          }
          {
            name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${azStorageAccountPrimaryAccessKey};FileEndpoint=<your-storage-account-file-endpoint>'
          }
        ]
        linuxFxVersion: linuxFXVersion[functionCombos[i].language] // Specifies a runtime
        alwaysOn: true
      }
      httpsOnly: true
    }
  }
]

// Assign RBAC roles (Key Vault Secrets User and Key Vault Crypto Officer) to the Function App's Managed Identity
resource keyVaultSecretsUserRoleAssignments 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = [
  for i in range(0, length(functionCombos)): {
    name: guid(functionApps[i].id, 'KeyVaultSecretsUser')
    properties: {
      principalId: functionApps[i].identity.principalId // Managed identity of the Function App
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'c1f2e3d4-5678-90ab-cdef-1234567890ab') // Key Vault Secrets User role
      principalType: 'ServicePrincipal'
    }
    scope: keyVault
  }
]

// Assign RBAC role for Key Vault Crypto Officer (for encryption and decryption)
resource keyVaultCryptoOfficerRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = [
  for i in range(0, length(functionCombos)): {
    name: guid(functionApps[i].id, 'KeyVaultCryptoOfficer')
    properties: {
      principalId: functionApps[i].identity.principalId // Managed identity of the Function App
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'a34f6265-4502-4602-a561-d72d34cb3fe9') // Key Vault Crypto Officer role
    }
    scope: keyVault
  }
]

/* may not need this 
// Ensure each function app has access to key vault
// Grant Key Vault access to the Function App's managed identity
resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2024-04-01-preview' = [
  for i in range(0, length(functionCombos)): {
    name: '${keyVault.name}-Policy-${functionCombos[i].full}'
    properties: {
      accessPolicies: [
        {
          tenantId: tenantId
          objectId: functionApps[i].identity.principalId // Managed identity of the Function App
          permissions: {
            secrets: [
              'get' // Permission to get secrets
              'list'
            ]
            keys: [
              'get' // Permission to get keys (if needed)
              'encrypt' // Permission to encrypt keys
              'decrypt' // Permission to decrypt keys
              'wrapKey' // Permission to wrap keys
              'unwrapKey' // Permission to unwrap keys
            ]
          }
        }
      ]
    }
  }
]
*/
// Establish different slots prod and staging for deployment on Azure
resource azFunctionSlotStagings 'Microsoft.Web/sites/slots@2024-04-01' = [
  for i in range(0, length(functionCombos)): {
    name: '${functionApps[i].name}/${functionAppStagingSlot}'
    location: location
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      enabled: true
      httpsOnly: true
    }
  }
]
