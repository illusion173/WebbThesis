#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

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
  },
  "customHandler": {
  "description": {
    "defaultExecutablePath": "handler",
    "workingDirectory": "",
    "arguments": []
  },
  "enableForwardingHttpRequest": true
}
}
'
FUNCTIONJSON='
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
'
# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do
    echo "Setting up project parent folder: $PROJECT"
    mkdir -p "$PROJECT"
    cd "$PROJECT" || exit
    # Initialize a Go module
    go mod init "$PROJECT"

    # Create host.json
    echo "$HOSTJSONFILE" > host.json

    # Install required dependencies
    go get github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys
    go get github.com/Azure/azure-sdk-for-go/sdk/azidentity
    go get golang.org/x/crypto/chacha20

    cat <<EOF > handler.go
package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
  "encoding/hex"
	"fmt"
	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys"
	"log"
	"os"
  "net/http"
  "io"
)


func handler(w http.ResponseWriter, r *http.Request) {

	var requestJSON map[string]string

	// Read the body fully
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}

	err = json.Unmarshal([]byte(body), &requestJSON)

	if err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	keyVaultURL := os.Getenv("AZURE_KEY_VAULT_URL")
	keyName := os.Getenv("_KEY_NAME")

	if keyVaultURL == "" || keyName == "" {
		http.Error(w, "Invalid function env vars missing something.", http.StatusBadRequest)
		return
	}

	// Authenticate with Azure
	cred, err := azidentity.NewDefaultAzureCredential(nil)

	if err != nil {
		http.Error(w, "Failed to authenticate with Azure", http.StatusInternalServerError)
		return
	}

	// Create Key Vault client
	client, err := azkeys.NewClient(keyVaultURL, cred, nil)
	if err != nil {
		http.Error(w, "Failed to create Key Vault client", http.StatusInternalServerError)
		return
	}


	algo := azkeys.SignatureAlgorithmES256
	algo_ptr := &algo


	operationParams := azkeys.SignParameters{
		Algorithm: algo_ptr,
		Value:     messageDigestBytes,
	}

	operationResult, err := client.Sign(context.TODO(), keyName, "", operationParams, nil)
	if err != nil {
		http.Error(w, "Failed to do operation ${PROJECT}", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"result": response})
}


func main() {
	http.HandleFunc("/api/${PROJECT}", handler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
EOF
    go mod tidy

    echo "Setting up project function folder: "
    PROJECTFUNCTIONFOLDER="go_${PROJECT}"
    mkdir -p "$PROJECTFUNCTIONFOLDER"

    cd "$PROJECTFUNCTIONFOLDER" || exit
    cat <<EOF > function.json
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
EOF
    cd ..

    ls -al
    cd ..
done

echo "Setup completed!"
