#!/bin/bash

# List of jar files
files=(
  "aes256_decrypt-1.0-SNAPSHOT.jar"
  "ecc256_verify-1.0-SNAPSHOT.jar"
  "rsa2048_decrypt-1.0-SNAPSHOT.jar"
  "rsa3072_encrypt-1.0-SNAPSHOT.jar"
  "sha256-1.0-SNAPSHOT.jar"
  "aes256_encrypt-1.0-SNAPSHOT.jar"
  "ecc384_sign-1.0-SNAPSHOT.jar"
  "rsa2048_encrypt-1.0-SNAPSHOT.jar"
  "rsa4096_decrypt-1.0-SNAPSHOT.jar"
  "sha384-1.0-SNAPSHOT.jar"
  "ecc256_sign-1.0-SNAPSHOT.jar"
  "ecc384_verify-1.0-SNAPSHOT.jar"
  "rsa3072_decrypt-1.0-SNAPSHOT.jar"
  "rsa4096_encrypt-1.0-SNAPSHOT.jar"
)

# Loop through each jar file
for file in "${files[@]}"; do
  # Extract the directory name before '-1.0-SNAPSHOT.jar'
  dir_name=$(echo "$file" | sed 's/-1.0-SNAPSHOT.jar//')

  # Create the directory if it doesn't exist
  mkdir -p "$dir_name"

  # Move the jar file to the directory
  mv "$file" "$dir_name/"
done
