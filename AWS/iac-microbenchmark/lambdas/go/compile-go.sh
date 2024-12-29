#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [arm|x86]"
    exit 1
fi

# Set architecture based on the argument
if [ "$1" == "x86" ]; then
    ARCH="amd64"
    COMPILE_DIR="x86"
elif [ "$1" == "arm" ]; then
    ARCH="arm64"
    COMPILE_DIR="arm"
else
    echo "Invalid argument. Use 'x86' or 'arm'."
    exit 1
fi

# Loop through every child directory
for dir in */; do
    if [ -d "$dir" ]; then
        # Change to the child directory
        cd "$dir" || exit

        # Compile for the chosen architecture
        GOOS=linux GOARCH=${ARCH} go build -tags lambda.norpc -o bootstrap main.go

        # Get the directory name without trailing slash
        dirname=$(basename "$dir")

        # Zip the bootstrap file with the directory name
        zip "${dirname}.zip" bootstrap

        mkdir -p "../${COMPILE_DIR}/${dirname}/"

        # Move the zip file to the parent directory's compiledgo folder for the specific architecture
        mv "${dirname}.zip" "../${COMPILE_DIR}/${dirname}/"


        # Clean up by removing the bootstrap file
        rm bootstrap
        

        # Return to the parent directory
        cd ..
    fi
done
# gross fix for above loop
rm -rf x86/x86/
rm -rf x86/arm
rm -rf arm/arm/
rm -rf arm/x86
