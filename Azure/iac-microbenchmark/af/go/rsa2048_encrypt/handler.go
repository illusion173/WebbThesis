package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
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

	keyVaultURL := os.Getenv("AZURE_KEY_VAULT_URL")
	keyName := os.Getenv("RSA2048_KEY_NAME")

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

	// Generate a random 256-bit AES key
	aesKey := make([]byte, 32) // 256-bit AES key
	_, err = rand.Read(aesKey)
	if err != nil {
		http.Error(w, "Failed to generate AES key", http.StatusInternalServerError)
		return
	}

	// Generate a random IV (16 bytes for AES-CTR)
	iv := make([]byte, aes.BlockSize)
	_, err = rand.Read(iv)
	if err != nil {
		http.Error(w, "Failed to generate IV", http.StatusInternalServerError)
		return
	}
	// Encrypt the message using AES-CTR
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		http.Error(w, "Failed to create AES cipher", http.StatusInternalServerError)
		return
	}

	message := requestJSON["message"]
	stream := cipher.NewCTR(block, iv)
	ciphertext := make([]byte, len(message))
	stream.XORKeyStream(ciphertext, []byte(message))
	algo := azkeys.EncryptionAlgorithmRSAOAEP256
	algo_ptr := &algo

	encryptParams := azkeys.KeyOperationParameters{
		Algorithm: algo_ptr,
		Value:     aesKey,
	}
	encryptResult, err := client.Encrypt(context.TODO(), keyName, "", encryptParams, nil)

	if err != nil {
		http.Error(w, "Failed to encrypt AES key with RSA-OAEP256", http.StatusInternalServerError)
		return
	}

	// Base64 encode the IV, ciphertext, and encrypted AES key for easy transport
	ivB64 := base64.StdEncoding.EncodeToString(iv)
	ciphertextB64 := base64.StdEncoding.EncodeToString(ciphertext)
	encryptedAesKeyB64 := base64.StdEncoding.EncodeToString(encryptResult.Result)

	// Output the result as JSON
	result := map[string]string{
		"iv":                ivB64,
		"ciphertext":        ciphertextB64,
		"encrypted_aes_key": encryptedAesKeyB64,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func main() {
	http.HandleFunc("/api/go_rsa2048_encrypt", handler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
