#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Define the zip directory
ZIPDIR="x86"

# Loop through each project
for PROJECT in "${PROJECTS[@]}"; do

    echo "Zipping up project: $PROJECT"

    # Ensure the project directory exists
    if [ ! -d "$PROJECT" ]; then
        echo "Skipping $PROJECT as the directory does not exist."
        continue
    fi

    # Create the zip file without including the top-level project folder
    (cd "$PROJECT" && zip -r "../${PROJECT}.zip" .)

    # Move the zip file to the x86 directory
    mv "${PROJECT}.zip" "$ZIPDIR/"

    echo "Done zipping ${PROJECT}."

done

echo "All projects have been zipped and moved to the ${ZIPDIR} directory."
