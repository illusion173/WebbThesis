#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do
    echo "Setting up project: $PROJECT"
    mkdir -p "$PROJECT"
    cd "$PROJECT" || exit

    # Initialize a Go module
    go mod init "$PROJECT"

    # Install required dependencies
    go get github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys
    go get github.com/Azure/azure-sdk-for-go/sdk/azidentity
    go get golang.org/x/crypto/chacha20

    touch main.go

    cd ..
done

echo "Setup completed!"
