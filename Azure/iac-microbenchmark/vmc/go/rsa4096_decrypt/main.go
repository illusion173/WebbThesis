package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
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

	// Extract the base64-encoded values
	ivB64 := requestJSON["iv"]
	ciphertextB64 := requestJSON["ciphertext"]
	encryptedAesKeyB64 := requestJSON["encrypted_aes_key"]

	// Decode base64 values into raw bytes
	iv, err := base64.StdEncoding.DecodeString(ivB64)
	if err != nil {
		log.Fatalf("Failed to decode IV: %v", err)
	}

	ciphertext, err := base64.StdEncoding.DecodeString(ciphertextB64)
	if err != nil {
		log.Fatalf("Failed to decode ciphertext: %v", err)
	}

	encryptedAesKey, err := base64.StdEncoding.DecodeString(encryptedAesKeyB64)
	if err != nil {
		log.Fatalf("Failed to decode encrypted AES key: %v", err)
	}

	// Get environment variables for Azure Key Vault
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

	algo := azkeys.EncryptionAlgorithmRSAOAEP256
	algo_ptr := &algo

	decryptParams := azkeys.KeyOperationParameters{
		Algorithm: algo_ptr,
		Value:     encryptedAesKey,
	}

	decryptResult, err := client.Decrypt(context.TODO(), keyName, "", decryptParams, nil)

	if err != nil {
		log.Fatalf("Failed to encrypt AES key with RSA-OAEP: %v", err)
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
	resultJSON, err := json.Marshal(result)
	if err != nil {
		log.Fatalf("Failed to marshal output JSON: %v", err)
	}

	fmt.Println(string(resultJSON))
}
