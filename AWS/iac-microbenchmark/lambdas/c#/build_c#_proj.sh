#!/bin/bash

# Array of directories to exclude
EXCLUDE_DIRS=("x86" "arm")

# Function to check if a directory should be excluded
should_exclude() {
    local dir="$1"
    for exclude in "${EXCLUDE_DIRS[@]}"; do
        if [[ "$dir" == "$exclude" ]]; then
            return 0  # True, should exclude
        fi
    done
    return 1  # False, should not exclude
}

# Check if a runtime argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <runtime>"
    echo "Please enter either linux-x64 or linux-arm64."
    exit 1
fi

# Assign the first argument to RUNTIME
RUNTIME="$1"


# Validate runtime input
if [[ "$RUNTIME" != "linux-x64" && "$RUNTIME" != "linux-arm64" ]]; then
    echo "Invalid runtime. Please enter either linux-x64 or linux-arm64."
    exit 1
fi

# Loop through all subdirectories in the current directory
for dir in */; do
    # Remove trailing slash from directory name

    dir=${dir%/}

    # Check if the directory should be excluded
    if should_exclude "$dir"; then
        echo "Skipping excluded directory: $dir"
        continue
    fi


    echo "Processing $dir"
    
    # Navigate to project root
    cd "$dir/src/$dir"
    
    # Build the project
    dotnet build -c Release -r $RUNTIME
    
    # Publish the project
    dotnet publish --configuration "Release" --framework "net8.0" /p:GenerateRuntimeConfigurationFiles=true --runtime "$RUNTIME" --self-contained False -o ./publish
    
    # Determine the target directory based on runtime
    if [ "$RUNTIME" == "linux-x64" ]; then
        TARGET_DIR="../../../../x86/${dir}"
        echo "TARGET DIRRRR"
        echo TARGET_DIR
    else
        TARGET_DIR="../../../../arm/${dir}"
    fi
    
    # Create the target directory if it doesn't exist
    mkdir -p "$TARGET_DIR"
    
    cd publish

    # Zip the publish directory
    zip -r "$TARGET_DIR/$dir.zip" .
    cd ..
    
    
    # Remove the publish folder
    rm -rf publish
    
    # Navigate back to the parent directory
    cd ../../../
    
    echo "Finished processing $dir"
    echo
done

echo "Build process completed for all projects."
