#!/bin/bash

# Variables
storage_account="storagebenchwebbeecserau"
container_name="function-releases"
output_file="blob_urls.json"

# Get the list of blobs in the container
blobs=$(az storage blob list \
  --account-name "$storage_account" \
  --container-name "$container_name" \
  --query "[].name" -o tsv)

# Initialize the JSON structure
echo "{" > "$output_file"

# Loop through each blob
first=true
for blob in $blobs; do
  # Remove the '.zip' suffix from the blob name
  blob_name_without_zip="${blob%.zip}"

  # Construct the URL for the blob
  blob_url="https://${storage_account}.blob.core.windows.net/${container_name}/${blob}"

  # Add the entry to the JSON file
  if $first; then
    echo "  \"$blob_name_without_zip\": \"$blob_url\"" >> "$output_file"
    first=false
  else
    echo ",\n  \"$blob_name_without_zip\": \"$blob_url\"" >> "$output_file"
  fi
done

# Close the JSON structure
echo "}" >> "$output_file"

echo "URLs have been saved to $output_file"
