// This bicep file serves as the infrastructure user input
// This is where one can determine the exact test functions one wants to create

// REQUIRED INPUTS:
// Storage account (string)
// Application Insights resource (string) where functions will report to
// The resource group where all the functions will be contained in

// Comment out which functions you do NOT want to create.
// Gross for now works, since nested for loops don't exist in bicep yet.
@description('List of all possible combinations of architecture, language, and operation as strings')
var functionComboStrings = [
  'x86-c#-aes256_decrypt'
  'x86-c#-aes256_encrypt'
  'x86-c#-ecc256_sign'
  'x86-c#-ecc256_verify'
  'x86-c#-ecc384_sign'
  'x86-c#-ecc384_verify'
  'x86-c#-rsa2048_decrypt'
  'x86-c#-rsa2048_encrypt'
  'x86-c#-rsa3072_decrypt'
  'x86-c#-rsa3072_encrypt'
  'x86-c#-rsa4096_decrypt'
  'x86-c#-rsa4096_encrypt'
  'x86-go-aes256_decrypt'
  'x86-go-aes256_encrypt'
  'x86-go-ecc256_sign'
  'x86-go-ecc256_verify'
  'x86-go-ecc384_sign'
  'x86-go-ecc384_verify'
  'x86-go-rsa2048_decrypt'
  'x86-go-rsa2048_encrypt'
  'x86-go-rsa3072_decrypt'
  'x86-go-rsa3072_encrypt'
  'x86-go-rsa4096_decrypt'
  'x86-go-rsa4096_encrypt'
  'x86-java-aes256_decrypt'
  'x86-java-aes256_encrypt'
  'x86-java-ecc256_sign'
  'x86-java-ecc256_verify'
  'x86-java-ecc384_sign'
  'x86-java-ecc384_verify'
  'x86-java-rsa2048_decrypt'
  'x86-java-rsa2048_encrypt'
  'x86-java-rsa3072_decrypt'
  'x86-java-rsa3072_encrypt'
  'x86-java-rsa4096_decrypt'
  'x86-java-rsa4096_encrypt'
  'x86-python-aes256_decrypt'
  'x86-python-aes256_encrypt'
  'x86-python-ecc256_sign'
  'x86-python-ecc256_verify'
  'x86-python-ecc384_sign'
  'x86-python-ecc384_verify'
  'x86-python-rsa2048_decrypt'
  'x86-python-rsa2048_encrypt'
  'x86-python-rsa3072_decrypt'
  'x86-python-rsa3072_encrypt'
  'x86-python-rsa4096_decrypt'
  'x86-python-rsa4096_encrypt'
  'x86-rust-aes256_decrypt'
  'x86-rust-aes256_encrypt'
  'x86-rust-ecc256_sign'
  'x86-rust-ecc256_verify'
  'x86-rust-ecc384_sign'
  'x86-rust-ecc384_verify'
  'x86-rust-rsa2048_decrypt'
  'x86-rust-rsa2048_encrypt'
  'x86-rust-rsa3072_decrypt'
  'x86-rust-rsa3072_encrypt'
  'x86-rust-rsa4096_decrypt'
  'x86-rust-rsa4096_encrypt'
  'x86-typescript-aes256_decrypt'
  'x86-typescript-aes256_encrypt'
  'x86-typescript-ecc256_sign'
  'x86-typescript-ecc256_verify'
  'x86-typescript-ecc384_sign'
  'x86-typescript-ecc384_verify'
  'x86-typescript-rsa2048_decrypt'
  'x86-typescript-rsa2048_encrypt'
  'x86-typescript-rsa3072_decrypt'
  'x86-typescript-rsa3072_encrypt'
  'x86-typescript-rsa4096_decrypt'
  'x86-typescript-rsa4096_encrypt'
  'arm-c#-aes256_decrypt'
  'arm-c#-aes256_encrypt'
  'arm-c#-ecc256_sign'
  'arm-c#-ecc256_verify'
  'arm-c#-ecc384_sign'
  'arm-c#-ecc384_verify'
  'arm-c#-rsa2048_decrypt'
  'arm-c#-rsa2048_encrypt'
  'arm-c#-rsa3072_decrypt'
  'arm-c#-rsa3072_encrypt'
  'arm-c#-rsa4096_decrypt'
  'arm-c#-rsa4096_encrypt'
  'arm-go-aes256_decrypt'
  'arm-go-aes256_encrypt'
  'arm-go-ecc256_sign'
  'arm-go-ecc256_verify'
  'arm-go-ecc384_sign'
  'arm-go-ecc384_verify'
  'arm-go-rsa2048_decrypt'
  'arm-go-rsa2048_encrypt'
  'arm-go-rsa3072_decrypt'
  'arm-go-rsa3072_encrypt'
  'arm-go-rsa4096_decrypt'
  'arm-go-rsa4096_encrypt'
  'arm-java-aes256_decrypt'
  'arm-java-aes256_encrypt'
  'arm-java-ecc256_sign'
  'arm-java-ecc256_verify'
  'arm-java-ecc384_sign'
  'arm-java-ecc384_verify'
  'arm-java-rsa2048_decrypt'
  'arm-java-rsa2048_encrypt'
  'arm-java-rsa3072_decrypt'
  'arm-java-rsa3072_encrypt'
  'arm-java-rsa4096_decrypt'
  'arm-java-rsa4096_encrypt'
  'arm-python-aes256_decrypt'
  'arm-python-aes256_encrypt'
  'arm-python-ecc256_sign'
  'arm-python-ecc256_verify'
  'arm-python-ecc384_sign'
  'arm-python-ecc384_verify'
  'arm-python-rsa2048_decrypt'
  'arm-python-rsa2048_encrypt'
  'arm-python-rsa3072_decrypt'
  'arm-python-rsa3072_encrypt'
  'arm-python-rsa4096_decrypt'
  'arm-python-rsa4096_encrypt'
  'arm-rust-aes256_decrypt'
  'arm-rust-aes256_encrypt'
  'arm-rust-ecc256_sign'
  'arm-rust-ecc256_verify'
  'arm-rust-ecc384_sign'
  'arm-rust-ecc384_verify'
  'arm-rust-rsa2048_decrypt'
  'arm-rust-rsa2048_encrypt'
  'arm-rust-rsa3072_decrypt'
  'arm-rust-rsa3072_encrypt'
  'arm-rust-rsa4096_decrypt'
  'arm-rust-rsa4096_encrypt'
  'arm-typescript-aes256_decrypt'
  'arm-typescript-aes256_encrypt'
  'arm-typescript-ecc256_sign'
  'arm-typescript-ecc256_verify'
  'arm-typescript-ecc384_sign'
  'arm-typescript-ecc384_verify'
  'arm-typescript-rsa2048_decrypt'
  'arm-typescript-rsa2048_encrypt'
  'arm-typescript-rsa3072_decrypt'
  'arm-typescript-rsa3072_encrypt'
  'arm-typescript-rsa4096_decrypt'
  'arm-typescript-rsa4096_encrypt'
]

@description('The set keyvault name, MUST BE SET')
@export()
var keyvaultname = ''

@description('The array of structs containining architecture, language, and operation of function.')
@export()
var functionCombos = [
  for combo in functionComboStrings: {
    architecture: split(combo, '-')[0]
    language: split(combo, '-')[1]
    operation: split(combo, '-')[2]
    full: combo
  }
]

@description('The runtime versions specific to each language.')
@export()
var linuxFXVersion = {
  java: 'JAVA|21'
  'c#': 'DOTNET|8.0'
  typescript: 'NODE|22' // 23 not available for right now
  python: 'Python|3.11'
  rust: 'Rust|1.83.0'
  go: 'Go|1.23'
}

@description('The runtime stacks specific to each language.')
@export()
var runtimeMap = {
  java: 'java'
  'c#': 'dotnet'
  typescript: 'node'
  python: 'python'
  rust: 'rust'
  go: 'go'
}
