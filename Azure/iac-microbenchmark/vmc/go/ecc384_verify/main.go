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

	// Extract the message digest and signature from the input
	messageDigestHex := requestJSON["message_digest"]
	signatureB64 := requestJSON["signature"]

	// Decode the message digest (from hex) and the signature (from base64)
	messageDigestBytes, err := hex.DecodeString(messageDigestHex)
	if err != nil {
		log.Fatalf("Failed to decode hex string for message digest: %v", err)
	}

	signatureBytes, err := base64.StdEncoding.DecodeString(signatureB64)
	if err != nil {
		log.Fatalf("Failed to decode base64 signature: %v", err)
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

	// Prepare the verification parameters
	algo := azkeys.SignatureAlgorithmES384
	algo_ptr := &algo

	// Create the Verify parameters
	verifyParams := azkeys.VerifyParameters{
		Algorithm: algo_ptr,
		Digest:    messageDigestBytes, // 32-byte message digest to verify
		Signature: signatureBytes,     // The signature to verify
	}

	// Perform the verification
	verifyResult, err := client.Verify(context.TODO(), keyName, "", verifyParams, nil)

	if err != nil {
		log.Fatalf("Failed to verify the signature: %v", err)
	}

	// Output the result of verification
	result := map[string]bool{"is_valid": *verifyResult.Value}

	resultJSON, err := json.Marshal(result)
	if err != nil {
		log.Fatalf("Failed to marshal output JSON: %v", err)
	}

	// Print the resulting JSON with the verification result
	fmt.Println(string(resultJSON))
}
