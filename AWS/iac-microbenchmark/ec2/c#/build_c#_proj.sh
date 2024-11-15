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

# Check if architecture is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <arch>"
    echo "Example: $0 x86 or $0 arm"
    exit 1
fi

arch_dir="$1"

# Validate arch_dir value
if [ "$arch_dir" != "x86" ] && [ "$arch_dir" != "arm" ]; then
    echo "Invalid architecture specified. Use 'x86' or 'arm'."
    exit 1
fi

# Store the parent directory
parent_dir=$(pwd)

# Create target directories if they do not exist
mkdir -p "./x86" "./arm"

# Loop through each project
for project in "${projects[@]}"; do
    if [ ! -d "$project" ]; then
        echo "Directory $project does not exist, skipping..."
        continue
    fi

    cd "$project" || exit 1  # Safely change directory

    echo "Building project: $project for architecture: $arch_dir..."

    # Determine the target directory based on runtime
    if [ "$arch_dir" == "x86" ]; then
        dotnet publish -c Release -r linux-x64 --self-contained true /p:PublishSingleFile=true
        cp -v bin/Release/net8.0/linux-x64/publish/$project ../x86/ 2>/dev/null
    else
        dotnet publish -c Release -r linux-arm64 --self-contained true /p:PublishSingleFile=true
        cp -v bin/Release/net8.0/linux-arm64/publish/$project ../arm/ 2>/dev/null
    fi

    # Return to the parent directory
    cd "$parent_dir" || exit 1

    echo "Project $project built and moved to $arch_dir."
done

echo "All projects created successfully."
