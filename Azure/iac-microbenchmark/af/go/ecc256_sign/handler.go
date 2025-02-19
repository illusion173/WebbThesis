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
	keyName := os.Getenv("ECC256_KEY_NAME")

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
	// Extract the message digest from the input
	messageDigest := requestJSON["message_digest"]

	messageDigestBytes, err := hex.DecodeString(messageDigest)
	if err != nil {
		log.Fatalf("Failed to decode hex string: %v", err)
	}

	operationParams := azkeys.SignParameters{
		Algorithm: algo_ptr,
		Value:     messageDigestBytes,
	}

	operationResult, err := client.Sign(context.TODO(), keyName, "", operationParams, nil)
	if err != nil {
		http.Error(w, "Failed to do operation ecc256_sign", http.StatusInternalServerError)
		return
	}

	resultSig := operationResult.Result

	// Base64 encode the signature for easy transport
	signatureB64 := base64.StdEncoding.EncodeToString(resultSig)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"signature": signatureB64})
}

func main() {
	http.HandleFunc("/api/go_ecc256_sign", handler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
