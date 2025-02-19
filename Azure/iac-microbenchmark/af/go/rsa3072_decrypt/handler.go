package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
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

	// Extract the base64-encoded values
	ivB64 := requestJSON["iv"]
	ciphertextB64 := requestJSON["ciphertext"]
	encryptedAesKeyB64 := requestJSON["encrypted_aes_key"]

	// Decode base64 values into raw bytes
	iv, err := base64.StdEncoding.DecodeString(ivB64)
	if err != nil {
		http.Error(w, "Failed to decode IV", http.StatusBadRequest)
		return
	}

	ciphertext, err := base64.StdEncoding.DecodeString(ciphertextB64)
	if err != nil {
		http.Error(w, "Failed to decode ciphertext", http.StatusBadRequest)
		return
	}

	encryptedAesKey, err := base64.StdEncoding.DecodeString(encryptedAesKeyB64)
	if err != nil {
		http.Error(w, "Failed to decode encrypted AES key", http.StatusBadRequest)
		return
	}

	keyVaultURL := os.Getenv("AZURE_KEY_VAULT_URL")
	keyName := os.Getenv("RSA3072_KEY_NAME")

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

	algo := azkeys.EncryptionAlgorithmRSAOAEP256
	algo_ptr := &algo

	decryptParams := azkeys.KeyOperationParameters{
		Algorithm: algo_ptr,
		Value:     encryptedAesKey,
	}

	decryptResult, err := client.Decrypt(context.TODO(), keyName, "", decryptParams, nil)

	if err != nil {
		http.Error(w, "Failed to decrypt AES key with RSA-OAEP256", http.StatusInternalServerError)
		return
	}

	aesKey := decryptResult.Result

	// Decrypt the ciphertext using AES-CTR
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		log.Fatalf("Failed to create AES cipher: %v", err)
	}
	stream := cipher.NewCTR(block, iv)
	plaintext := make([]byte, len(ciphertext))
	stream.XORKeyStream(plaintext, ciphertext)

	// Output the decrypted message
	result := map[string]string{"decrypted_message": string(plaintext)}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func main() {
	http.HandleFunc("/api/go_rsa3072_decrypt", handler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
