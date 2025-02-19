// This bicep file serves as the infrastructure user input
// This is where one can determine the exact test functions one wants to create

// REQUIRED INPUTS:
// Storage account (string)
// Application Insights resource (string) where functions will report to
// The resource group where all the functions will be contained in

// Comment out which functions you do NOT want to create.
// Gross for now works, since nested for loops don't exist in bicep yet.
@export()
@description('List of all possible combinations of  language, and operation as strings')
var functionComboStrings = [
  //'dotnet-ecc256sign'
  //'dotnet-ecc256verify'
  //'dotnet-ecc384sign'
  //'dotnet-ecc384verify'
  //'dotnet-rsa2048decrypt'
  //'dotnet-rsa2048encrypt'
  //'dotnet-rsa3072decrypt'
  //'dotnet-rsa3072encrypt'
  //'dotnet-rsa4096decrypt'
  //'dotnet-rsa4096encrypt'
  //'go-ecc256sign'
  //'go-ecc256verify'
  //'go-ecc384sign'
  //'go-ecc384verify'
  //'go-rsa2048decrypt'
  //'go-rsa2048encrypt'
  //'go-rsa3072decrypt'
  //'go-rsa3072encrypt'
  //'go-rsa4096decrypt'
  //'go-rsa4096encrypt'
  'java-ecc256sign'
  'java-ecc256verify'
  'java-ecc384sign'
  'java-ecc384verify'
  'java-rsa2048decrypt'
  'java-rsa2048encrypt'
  'java-rsa3072decrypt'
  'java-rsa3072encrypt'
  'java-rsa4096decrypt'
  'java-rsa4096encrypt'
  //'python-ecc256sign'
  //'python-ecc256verify'
  //'python-ecc384sign'
  //'python-ecc384verify'
  //'python-rsa2048decrypt'
  //'python-rsa2048encrypt'
  //'python-rsa3072decrypt'
  //'python-rsa3072encrypt'
  //'python-rsa4096decrypt'
  //'python-rsa4096encrypt'
  //'typescript-ecc256sign'
  //'typescript-ecc256verify'
  //'typescript-ecc384sign'
  //'typescript-ecc384verify'
  //'typescript-rsa2048decrypt'
  //'typescript-rsa2048encrypt'
  //'typescript-rsa3072decrypt'
  //'typescript-rsa3072encrypt'
  //'typescript-rsa4096decrypt'
  //'typescript-rsa4096encrypt'
]

var functionBlobWebsiteRunPackage = {
  'dotnet-ecc256sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_ecc256_sign.zip'
  'dotnet-ecc256verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_ecc256_verify.zip'
  'dotnet-ecc384sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_ecc384_sign.zip'
  'dotnet-ecc384verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_ecc384_verify.zip'
  'dotnet-rsa2048decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa2048_decrypt.zip'
  'dotnet-rsa2048encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa2048_encrypt.zip'
  'dotnet-rsa3072decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa3072_decrypt.zip'
  'dotnet-rsa3072encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa3072_encrypt.zip'
  'dotnet-rsa4096decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa4096_decrypt.zip'
  'dotnet-rsa4096encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/dotnet_rsa4096_encrypt.zip'
  'go-ecc256sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_ecc256_sign.zip'
  'go-ecc256verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_ecc256_verify.zip'
  'go-ecc384sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_ecc384_sign.zip'
  'go-ecc384verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_ecc384_verify.zip'
  'go-rsa2048decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa2048_decrypt.zip'
  'go-rsa2048encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa2048_encrypt.zip'
  'go-rsa3072decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa3072_decrypt.zip'
  'go-rsa3072encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa3072_encrypt.zip'
  'go-rsa4096decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa4096_decrypt.zip'
  'go-rsa4096encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/go_rsa4096_encrypt.zip'
  'java-ecc256sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_ecc256_sign.zip'
  'java-ecc256verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_ecc256_verify.zip'
  'java-ecc384sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_ecc384_sign.zip'
  'java-ecc384verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_ecc384_verify.zip'
  'java-rsa2048decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa2048_decrypt.zip'
  'java-rsa2048encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa2048_encrypt.zip'
  'java-rsa3072decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa3072_decrypt.zip'
  'java-rsa3072encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa3072_encrypt.zip'
  'java-rsa4096decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa4096_decrypt.zip'
  'java-rsa4096encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/java_rsa4096_encrypt.zip'
  'python-ecc256sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_ecc256_sign.zip'
  'python-ecc256verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_ecc256_verify.zip'
  'python-ecc384sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_ecc384_sign.zip'
  'python-ecc384verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_ecc384_verify.zip'
  'python-rsa2048decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa2048_decrypt.zip'
  'python-rsa2048encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa2048_encrypt.zip'
  'python-rsa3072decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa3072_decrypt.zip'
  'python-rsa3072encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa3072_encrypt.zip'
  'python-rsa4096decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa4096_decrypt.zip'
  'python-rsa4096encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/python_rsa4096_encrypt.zip'
  'typescript-ecc256sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_ecc256_sign.zip'
  'typescript-ecc256verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_ecc256_verify.zip'
  'typescript-ecc384sign': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_ecc384_sign.zip'
  'typescript-ecc384verify': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_ecc384_verify.zip'
  'typescript-rsa2048decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa2048_decrypt.zip'
  'typescript-rsa2048encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa2048_encrypt.zip'
  'typescript-rsa3072decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa3072_decrypt.zip'
  'typescript-rsa3072encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa3072_encrypt.zip'
  'typescript-rsa4096decrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa4096_decrypt.zip'
  'typescript-rsa4096encrypt': 'https://storagebenchwebbeecserau.blob.core.windows.net/function-releases/typescript_rsa4096_encrypt.zip'
}

@export()
var keyvaultname = 'AzBenchmarkKvWebb'

@export()
var azure_key_vault_url = 'https://azbenchmarkkvwebb.vault.azure.net/'

@description('The array of structs containining architecture, language, and operation of function.')
@export()
var functionCombos = [
  for combo in functionComboStrings: {
    language: split(combo, '-')[0]
    operation: split(combo, '-')[1]
    blob_url: functionBlobWebsiteRunPackage[combo]
    full: combo
  }
]

//linuxFXVersion setting map 
@description('The runtime versions specific to each language.')
@export()
var linuxFXVersion = {
  java: 'Java|21'
  dotnet: 'DOTNET-ISOLATED|8.0'
  typescript: 'Node|22' // 23 not available for right now
  python: 'Python|3.11'
}

// FUNCTIONSWORKER_RUNTIME_MAP
@description('The runtime stacks specific to each language.')
@export()
var runtimeMap = {
  java: 'java'
  dotnet: 'dotnet-isolated'
  typescript: 'node'
  python: 'python'
  go: 'custom'
}
