#!/bin/bash



# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")


REQUIREMENTSTXT='asyncio==3.4.3
azure-core==1.32.0
azure-functions=1.21.3
azure-identity==1.19.0
azure-keyvault-keys==4.10.0
certifi==2024.12.14
cffi==1.17.1
charset-normalizer==3.4.1
cryptography==44.0.0
idna==3.10
isodate==0.7.2
msal==1.31.1
msal-extensions==1.2.0
portalocker==2.10.1
pycparser==2.22
PyJWT==2.10.1
requests==2.32.3
six==1.17.0
typing_extensions==4.12.2
urllib3==2.3.0
'
HOSTJSONFILE='{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
'

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do

    echo "Setting up project: $PROJECT"
    mkdir -p $PROJECT
    # go into new project
    cd "$PROJECT" || exit

    # Create requirements.txt
    echo "$REQUIREMENTSTXT" > requirements.txt

    # Create host.json
    echo "$HOSTJSONFILE" > host.json

    # initialize files
    # this is where the "main handler function is initialized."
    cat <<EOF > function_app.py
import logging
import os
import sys
import base64
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm, SignatureAlgorithm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="python_${PROJECT}")
@app.route(route="${PROJECT}")
def httptriggerbench(req: func.HttpRequest) -> func.HttpResponse:

    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["_KEY_NAME"]

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for ${PROJECT} is missing body.", status_code=400)



    # main code here
    try:
        print("")

        # Authenticate using default azure creds in azure function
        credential = DefaultAzureCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Get the key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client for operation
        crypto_client = CryptographyClient(key, credential)

        result_json_str = json.dumps({"item": "item"})

        return func.HttpResponse(f"{result_json_str}")
    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation ${PROJECT} {e} .", status_code=500)
EOF



    echo "Done building ${PROJECT}"
    # return parent
    cd ..

done

echo "Done preparing Python Azure Functions."



