#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Check for user input for architecture
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <architecture>"
    echo "Architecture should be either 'x86' or 'arm'."
    exit 1
fi

ARCH=$1

# Check if the input is valid
if [[ "$ARCH" != "x86" && "$ARCH" != "arm" ]]; then
    echo "Invalid architecture: $ARCH"
    echo "Please provide either 'x86' or 'arm'."
    exit 1
fi

BASE_DIR=$(pwd)

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do

    # Change to the project directory
    cd $PROJECT || continue
    ls


    # Build the package
    mvn clean package

    cd target
    cp "${PROJECT}-1.0-SNAPSHOT.jar" ../../$ARCH
 
    # Go back to the base directory
    cd "$BASE_DIR" || exit


done


echo "Done!"
