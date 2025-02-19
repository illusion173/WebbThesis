#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Define the zip directory
ZIPDIR="x86"
PARENTDIR="$PWD"
# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do

    echo "Building $PROJECT..."
    cd "java_$PROJECT" || exit

    # Build package but skip tests
    mvn package -Dmaven.test.skip

    cd target/azure-functions/java_${PROJECT}
    zip -r "$PARENTDIR/$ZIPDIR/${PROJECT}.zip" ./*

    # Return to parent
    cd $PARENTDIR
done
echo "Finished building and zipping up Java Projects!"
