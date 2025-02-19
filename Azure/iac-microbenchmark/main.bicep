import {
  functionCombos
  linuxFXVersion
  runtimeMap
  keyvaultname
  azure_key_vault_url
} from 'iac-inputs.bicep'

param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'storagebenchwebbeecserau'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

// Assuming you have your storage account resource
var azStorageAccountPrimaryAccessKey = listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'consumptionplan-webbeecserau'
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
  name: 'benchmarkAppInsight-webbeecserau'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

var azAppInsightsInstrumentationKey = appInsight.properties.InstrumentationKey

// Reference the existing Key Vault, forces user to create the keys themselves, intentional
resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' existing = {
  name: keyvaultname // Replace with your existing Key Vault name
}

@batchSize(5)
resource functionApps 'Microsoft.Web/sites@2022-09-01' = [
  for i in range(0, length(functionCombos)): {
    name: '${functionCombos[i].language}${functionCombos[i].operation}benchmarkappwebbeecserau'
    location: location
    kind: 'functionapp'
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      serverFarmId: appServicePlan.id
      httpsOnly: true
      siteConfig: {
        //comment the linuxFXVersion for go deployment. 
        linuxFxVersion: linuxFXVersion[functionCombos[i].language]
        appSettings: [
          {
            name: 'AzureWebJobsStorage'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${azStorageAccountPrimaryAccessKey}'
          }
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: 'InstrumentationKey=${azAppInsightsInstrumentationKey}'
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
            name: 'WEBSITE_RUN_FROM_PACKAGE'
            value: functionCombos[i].blob_url
          }
          {
            name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
            value: 'true'
          }
          {
            name: 'WEBSITES_PORT'
            value: '8080'
          }
          {
            name: 'WEBSITE_CONTENTSHARE'
            value: '${functionCombos[i].language}${functionCombos[i].operation}benchmarkappwebbeecserau'
          }
          {
            name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${azStorageAccountPrimaryAccessKey}'
          }
          {
            name: 'AZURE_KEY_VAULT_URL'
            value: azure_key_vault_url
          }
          { name: 'ECC256_KEY_NAME', value: 'ecc256benchmark' }
          { name: 'ECC384_KEY_NAME', value: 'ecc384benchmark-2' }
          { name: 'RSA2048_KEY_NAME', value: 'rsa2048benchmark' }
          { name: 'RSA3072_KEY_NAME', value: 'rsa3072benchmark' }
          { name: 'RSA4096_KEY_NAME', value: 'rsa4096benchmark' }
        ]
      }
    }
  }
]

@batchSize(5)
// Assign RBAC roles (Key Vault Secrets User and Key Vault Crypto Officer) to the Function App's Managed Identity
resource keyVaultSecretsUserRoleAssignments 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = [
  for i in range(0, length(functionCombos)): {
    name: guid(functionApps[i].id, 'KeyVaultSecretsOfficer')
    properties: {
      principalId: functionApps[i].identity.principalId
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
      principalType: 'ServicePrincipal'
    }
    scope: keyVault
    dependsOn: [functionApps]
  }
]

@batchSize(5)
// Assign RBAC role for Key Vault Crypto Officer (for encryption and decryption)
resource keyVaultCryptoOfficerRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = [
  for i in range(0, length(functionCombos)): {
    name: guid(functionApps[i].id, 'KeyVaultCryptoOfficer')
    properties: {
      principalId: functionApps[i].identity.principalId
      roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '14b46e9e-c2b7-41b4-b07b-48a6ebf60603')
      principalType: 'ServicePrincipal'
    }
    scope: keyVault
    dependsOn: [functionApps]
  }
]
