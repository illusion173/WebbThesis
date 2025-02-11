package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys"
	"log"
	"os"
)

func main() {

	// Parse the input JSON argument (get the message to encrypt)
	requestJSONRaw := os.Args[1]
	var requestJSON map[string]string
	err := json.Unmarshal([]byte(requestJSONRaw), &requestJSON)
	if err != nil {
		log.Fatalf("Error parsing input JSON: %v", err)
	}

	message := requestJSON["message"]

	// Generate a random 256-bit AES key
	aesKey := make([]byte, 32) // 256-bit AES key
	_, err = rand.Read(aesKey)
	if err != nil {
		log.Fatalf("Failed to generate AES key: %v", err)
	}

	// Generate a random IV (16 bytes for AES-CTR)
	iv := make([]byte, aes.BlockSize)
	_, err = rand.Read(iv)
	if err != nil {
		log.Fatalf("Failed to generate IV: %v", err)
	}

	// Azure Key Vault configurations
	keyVaultURL := os.Getenv("AZURE_KEY_VAULT_URL")
	keyName := os.Getenv("RSA4096_KEY_NAME")

	if keyVaultURL == "" || keyName == "" {
		log.Fatal("AZURE_KEY_VAULT_URL and RSA4096_KEY_NAME environment variables must be set.")
	}

	// Authenticate with Azure
	cred, err := azidentity.NewAzureCLICredential(nil)
	if err != nil {
		log.Fatalf("Failed to authenticate with Azure: %v", err)
	}

	// Create Key Vault client
	client, err := azkeys.NewClient(keyVaultURL, cred, nil)
	if err != nil {
		log.Fatalf("Failed to create Key Vault client: %v", err)
	}

	// Encrypt the message using AES-CTR
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		log.Fatalf("Failed to create AES cipher: %v", err)
	}
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
		log.Fatalf("Failed to encrypt AES key with RSA-OAEP: %v", err)
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
	resultJSON, err := json.Marshal(result)
	if err != nil {
		log.Fatalf("Failed to marshal output JSON: %v", err)
	}

	// Print the resulting JSON with the encrypted data
	fmt.Println(string(resultJSON))
}
