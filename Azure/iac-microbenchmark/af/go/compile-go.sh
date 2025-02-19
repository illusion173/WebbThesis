#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Define the zip directory
ZIPDIR="x86"

# Create the zip directory if it doesn't exist
mkdir -p "$ZIPDIR"

# Compile each project
for PROJECT in "${PROJECTS[@]}"; do
    echo "Building $PROJECT..."
    cd "$PROJECT" || exit

    # Run Go build
    go build handler.go

    # Zip the contents of the project directory (excluding the project folder itself)
    zip -r "../$ZIPDIR/$PROJECT.zip" ./*

    echo "Done zipping ${PROJECT}."

    cd ..
done

echo "All projects have been zipped and moved to the ${ZIPDIR} directory."
