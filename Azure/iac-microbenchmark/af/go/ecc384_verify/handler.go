package main

import (
	"context"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys"
	"io"
	"log"
	"net/http"
	"os"
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
	keyName := os.Getenv("ECC384_KEY_NAME")

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

	algo := azkeys.SignatureAlgorithmES384
	algo_ptr := &algo

	// Extract the message digest and signature from the input
	messageDigestHex := requestJSON["message_digest"]
	signatureB64 := requestJSON["signature"]

	// Decode the message digest (from hex) and the signature (from base64)
	messageDigestBytes, err := hex.DecodeString(messageDigestHex)
	if err != nil {
		http.Error(w, "Failed to decode hex string for message digest", http.StatusInternalServerError)
		return
	}

	signatureBytes, err := base64.StdEncoding.DecodeString(signatureB64)

	if err != nil {
		http.Error(w, "Failed to decode base64 signature", http.StatusInternalServerError)
		return
	}

	operationParams := azkeys.VerifyParameters{
		Algorithm: algo_ptr,
		Digest:    messageDigestBytes,
		Signature: signatureBytes,
	}

	operationResult, err := client.Verify(context.TODO(), keyName, "", operationParams, nil)
	if err != nil {
		http.Error(w, "Failed to do operation ecc384_verify", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]bool{"is_valid": *operationResult.Value})
}

func main() {
	http.HandleFunc("/api/go_ecc384_verify", handler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
