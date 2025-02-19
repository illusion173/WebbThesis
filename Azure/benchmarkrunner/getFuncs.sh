#!/bin/bash

# Create an empty JSON object to hold the function names and URLs
json_output="{}"

PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")
LANGAUGES=("dotnet" "python" "java" "typescript")
RESOURCEGROUP="benchmarkWebbRG"

for LANGUAGE in "${LANGAUGES[@]}"; do
  for PROJECT in "${PROJECTS[@]}"; do
      function_name="${LANGUAGE}_${PROJECT}"
      cleaned_proj_op="${PROJECT//_/}"
      app_name="${LANGUAGE}${cleaned_proj_op}"
        # We will first cd to the parent language dir.
        if [[ "$LANGUAGE" == "dotnet" ]]; then
            function_name="${LANGUAGE}_${PROJECT}_program"
        fi
        echo $function_name
        echo $app_name
        echo $cleaned_proj_op
      #az functionapp function show --function-name ${function_name} --name ${app_name}benchmarkappwebbeecserau --resource-group $RESOURCEGROUP --query "invokeUrlTemplate" --output tsv
      url=$(az functionapp function show --function-name ${function_name} --name ${app_name}benchmarkappwebbeecserau --resource-group $RESOURCEGROUP --query "invokeUrlTemplate" --output tsv)
      #url=$(az functionapp function show --function-name ${function_name} --name ${LANGUAGE}${cleaned_proj_op}benchmarkappwebbeecserau --resource-group ${RESOURCEGROUP} --query "invokeUrlTemplate" --output tsv)
      echo $url
      # Update the JSON object with the function name as the key and the URL as the value
      json_output=$(echo "$json_output" | jq --arg function_name ${function_name} --arg url "$url" \
            '. + {($function_name): $url}')
      
    done

  done
echo "$json_output" > function_urls.json
