package main

import (
	"context"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys"
)

func main() {
	// Parse the input JSON argument
	requestJSONRaw := os.Args[1]
	var requestJSON map[string]string
	err := json.Unmarshal([]byte(requestJSONRaw), &requestJSON)
	if err != nil {
		log.Fatalf("Error parsing input JSON: %v", err)
	}

	// Extract the message digest from the input
	messageDigest := requestJSON["message_digest"]

	messageDigestBytes, err := hex.DecodeString(messageDigest)
	if err != nil {
		log.Fatalf("Failed to decode hex string: %v", err)
	}
	// Get environment variables for Azure Key Vault
	keyVaultURL := os.Getenv("AZURE_KEY_VAULT_URL")
	keyName := os.Getenv("ECC384_KEY_NAME")

	if keyVaultURL == "" || keyName == "" {
		log.Fatal("AZURE_KEY_VAULT_URL and ECC384_KEY_NAME environment variables must be set.")
	}

	// Authenticate with Azure
	cred, err := azidentity.NewDefaultAzureCredential(nil)
	if err != nil {
		log.Fatalf("Failed to authenticate with Azure: %v", err)
	}

	// Create Key Vault client
	client, err := azkeys.NewClient(keyVaultURL, cred, nil)
	if err != nil {
		log.Fatalf("Failed to create Key Vault client: %v", err)
	}

	algo := azkeys.SignatureAlgorithmES384
	algo_ptr := &algo

	signParams := azkeys.SignParameters{
		Algorithm: algo_ptr,
		Value:     messageDigestBytes,
	}

	signResult, err := client.Sign(context.TODO(), keyName, "", signParams, nil)
	if err != nil {
		log.Fatalf("Failed to sign the message digest: %v", err)
	}

	resultSignature := signResult.Result
	// Base64 encode the signature for easy transport
	signatureB64 := base64.StdEncoding.EncodeToString(resultSignature)

	// Output the signature in JSON format
	result := map[string]string{"signature": signatureB64}
	resultJSON, err := json.Marshal(result)
	if err != nil {
		log.Fatalf("Failed to marshal output JSON: %v", err)
	}

	// Print the resulting JSON with the signature
	fmt.Println(string(resultJSON))
}
