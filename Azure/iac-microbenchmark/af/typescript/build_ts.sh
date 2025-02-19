#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Define the zip directory
ZIPDIR="x86"

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do

    echo "Building $PROJECT..."
    cd "$PROJECT" || exit

    npm run build

    # Zip the contents of the project directory (excluding the project folder itself)
    zip -r "../$ZIPDIR/$PROJECT.zip" ./* -x "node_modules/*"
    echo "Done zipping ${PROJECT}."

    cd ..


done
echo "Finished Zipping up Typescript Projects!"
