#!/bin/bash

# Create a bin directory to store compiled executables
BIN_DIR=$1

mkdir -p "$BIN_DIR"

# List of projects to compile
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Compile each project
for PROJECT in "${PROJECTS[@]}"; do
    echo "Building $PROJECT..."
    cd "$PROJECT" || exit

    # Build the project and place the binary in the bin directory
    go build -o "../$1/$PROJECT"

    cd ..
done

echo "Build completed! Executables are in the $1 directory."
