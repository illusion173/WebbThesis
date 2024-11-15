#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [arm|x86]"
    exit 1
fi

# Set architecture based on the argument
if [ "$1" == "x86" ]; then
    ARCH="x86"
elif [ "$1" == "arm" ]; then
    ARCH="arm"
else
    echo "Invalid argument. Use 'x86' or 'arm'."
    exit 1
fi

TARGET_DIR="../${ARCH}"
# Loop through each child directory
for dir in */; do
    # Check if it is a directory
    if [ -d "$dir" ]; then
        echo "Building project in directory: $dir"

        # Navigate into the directory
        cd "$dir"

        # Run go build to create the executable
        if go build -o "${dir%/}"; then
            echo "Build successful for $dir"

            # Move the executable to the target directory
            mv "${dir%/}" "$TARGET_DIR"
            echo "Moved ${dir%/}.exe to $TARGET_DIR"
        else
            echo "Build failed for $dir"
        fi

        # Navigate back to the parent directory
        cd ..
    fi
done

echo "All projects have been processed."
