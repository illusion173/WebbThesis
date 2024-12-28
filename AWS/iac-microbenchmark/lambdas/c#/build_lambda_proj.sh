#!/bin/bash
# Assign the first argument to RUNTIME
RUNTIME="$1"
DESTINATION="$2"

# Validate runtime input
if [[ "$RUNTIME" != "linux-x64" && "$RUNTIME" != "linux-arm64" ]]; then
    echo "Invalid runtime. Please enter either linux-x64 or linux-arm64."
    exit 1
fi

# List of specific directories to process (add directories you want to analyze here)
DIRECTORIES_TO_PROCESS=(
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
    "ecc384_verify")  # Replace with actual directory names

# Traverse through each specified directory in the list
for dir in "${DIRECTORIES_TO_PROCESS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"
        cd "$dir/src/$dir"

        # Build the project
        dotnet build -c Release

        # Publish the project
        dotnet publish --configuration "Release" --framework "net8.0" /p:GenerateRuntimeConfigurationFiles=true --runtime "$RUNTIME" --self-contained False -o ./publish

        TARGET_DIR="../../../../$DESTINATION"

        cd publish

        # Create a ZIP archive of the published output
        zip -r "$TARGET_DIR/$dir.zip" .
        cd ..
        rm -rf publish
        cd ../../../
    else
        echo "Directory not found: $dir, skipping..."
    fi
done

echo "Build process completed for specified projects."

