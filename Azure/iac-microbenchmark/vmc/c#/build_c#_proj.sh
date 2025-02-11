#!/bin/bash

# Array of project directory names
projects=(
    "rsa2048_decrypt"
    "rsa2048_encrypt"
    "rsa3072_decrypt"
    "rsa3072_encrypt"
    "rsa4096_decrypt"
    "rsa4096_encrypt"
    "ecc256_sign"
    "ecc256_verify"
    "ecc384_sign"
    "ecc384_verify"
)

# Store the parent directory
parent_dir=$(pwd)


# Loop through each project
for project in "${projects[@]}"
do

    cd "$parent_dir" || exit 1  # Ensure you return to the parent directory
    echo "Project $project built."
done

echo "All projects built."
