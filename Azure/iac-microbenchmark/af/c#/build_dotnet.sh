#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")
PARENTDIR="$PWD"
ZIPDIR="x86"

for PROJECT in "${PROJECTS[@]}"; do
    echo "Building & Zipping project: $PROJECT"

    cd dotnet_$PROJECT
    dotnet publish -c Release -r linux-x64 -p:PublishReadyToRun=true

    cd bin/Release/net8.0/linux-x64/publish/


    zip -r "$PARENTDIR/$ZIPDIR/${PROJECT}.zip" ./*


    cd $PARENTDIR
done
