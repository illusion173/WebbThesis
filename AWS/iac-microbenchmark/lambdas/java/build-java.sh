#!/bin/bash

# Check for user input for architecture
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <architecture>"
    echo "Architecture should be either 'x86' or 'arm'."
    exit 1
fi

ARCH=$1

# Check if the input is valid
if [[ "$ARCH" != "x86" && "$ARCH" != "arm" ]]; then
    echo "Invalid architecture: $ARCH"
    echo "Please provide either 'x86' or 'arm'."
    exit 1
fi

# Get the current working directory
BASE_DIR=$(pwd)
# Define the target architecture directory in the parent directory
ARCH_DIR="$BASE_DIR/$ARCH"

# Check if the architecture directory exists
if [[ ! -d "$ARCH_DIR" ]]; then
    echo "Error: The directory $ARCH_DIR does not exist."
    exit 1
fi

# Loop through each directory in the base directory
for dir in "$BASE_DIR"/*; do
    if [[ -d "$dir" ]]; then
        echo "Processing directory: $dir"
        
        # Skip the x86 and arm directories
        if [[ "$(basename "$dir")" == "x86" || "$(basename "$dir")" == "arm" ]]; then
            echo "Skipping architecture directory: $dir"
            continue
        fi
        
        # Change to the project directory
        cd "$dir" || continue

        # Run Maven clean package
        mvn clean package
        
        # Define the jar file name based on the current directory name
        PROJECT_NAME=$(basename "$dir")
        JAR_FILE="${PROJECT_NAME}-1.0-SNAPSHOT.jar"
        
        # Check if the jar file exists
        if [[ -f "target/$JAR_FILE" ]]; then
            echo "Copying $JAR_FILE to $ARCH directory."
            mkdir -p "$ARCH_DIR/$PROJECT_NAME"
            cp "target/$JAR_FILE" "$ARCH_DIR/$PROJECT_NAME"
        else
            echo "Warning: $JAR_FILE not found in $dir/target."
        fi

        # Go back to the base directory
        cd "$BASE_DIR" || exit
    else
        echo "Skipping $dir: Not a valid Maven project."
    fi
done

echo "Done!"
