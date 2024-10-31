#!/bin/bash

# Array of project directory names
projects=(
    "rsa2048_decrypt"
    "rsa2048_encrypt"
    "rsa3072_decrypt"
    "rsa3072_encrypt"
    "rsa4096_decrypt"
    "rsa4096_encrypt"
    "sha256"
    "sha384"
    "aes256_decrypt"
    "aes256_encrypt"
    "ecc256_sign"
    "ecc256_verify"
    "ecc384_sign"
    "ecc384_verify"
)

arch_dir = "$1"

# Store the parent directory
parent_dir=$(pwd)


# Loop through each project
for project in "${projects[@]}"
do

    cd "$project/" || continue  # Safely change directory

    # Determine the target directory based on runtime
    if [ "$arch_dir" == "x86" ]; then
      dotnet publish -c Release -r linux-x64 --self-contained true /p:PublishSingleFile=true
      cp bin/Release/net8.0/linux-x64/publish/$project ../x86/
    else
      dotnet publish -c Release -r linux-arm64 --self-contained true /p:PublishSingleFile=true
      cp bin/Release/net8.0/linux-arm64/publish/$project ../arm/
    fi

    cd "$parent_dir" || exit 1  # Ensure you return to the parent directory

    echo "Project $project built and moved to $arch_dir."
done

echo "All projects created."
