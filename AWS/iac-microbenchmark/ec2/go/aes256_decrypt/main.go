// main.go
package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kms"
)

type EncryptedRequest struct {
	Ciphertext   string `json:"encrypted_message"`
	EncryptedAesKey string `json:"encrypted_data_key"`
	IV           string `json:"iv"`
	Tag          string `json:"tag"`
}

type DecryptedResponse struct {
	Message string `json:"message"`
	Error   string `json:"error,omitempty"`
}

func main() {
	// Get the JSON input from command line argument
	if len(os.Args) < 2 {
		fmt.Println(`{"error": "Missing JSON input"}`)
		return
	}
	requestJSONRaw := os.Args[1]

	var encryptedRequest EncryptedRequest
	if err := json.Unmarshal([]byte(requestJSONRaw), &encryptedRequest); err != nil {
		fmt.Println(`{"error": "Invalid request body"}`)
		return
	}

	// Decode Base64 fields
	ciphertext, err := base64.StdEncoding.DecodeString(encryptedRequest.Ciphertext)
	if err != nil {
		fmt.Println(`{"error": "Failed to decode ciphertext"}`)
		return
	}
	encrypted_aes_key, err := base64.StdEncoding.DecodeString(encryptedRequest.EncryptedAesKey)
	if err != nil {
		fmt.Println(`{"error": "Failed to decode encrypted key"}`)
		return
	}
	iv, err := base64.StdEncoding.DecodeString(encryptedRequest.IV)
	if err != nil {
		fmt.Println(`{"error": "Failed to decode IV"}`)
		return
	}
	tag, err := base64.StdEncoding.DecodeString(encryptedRequest.Tag)
	if err != nil {
		fmt.Println(`{"error": "Failed to decode tag"}`)
		return
	}

	// Create a top-level context
	ctx := context.Background()

	// Load AWS configuration
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		fmt.Println(`{"error": "Failed to load AWS config"}`)
		return
	}

	// Initialize the KMS client
	kmsClient := kms.NewFromConfig(cfg)

	// Get the KMS key ARN from environment variables
	kmsKeyID := os.Getenv("AES_KMS_KEY_ARN")
	if kmsKeyID == "" {
		fmt.Println(`{"error": "KMS key ARN not set"}`)
		return
	}

	// Decrypt the data key using KMS
	decryptedKeyOutput, err := kmsClient.Decrypt(ctx, &kms.DecryptInput{
		CiphertextBlob: encrypted_aes_key,
		KeyId:          aws.String(kmsKeyID),
	})
	if err != nil {
		fmt.Printf(`{"error": "Failed to decrypt data key: %v"}`, err)
		return
	}

	// Decrypt the message using AES-GCM
	plaintextMessage, err := decryptMessageWithAESGCM(decryptedKeyOutput.Plaintext, ciphertext, iv, tag)
	if err != nil {
		fmt.Printf(`{"error": "Failed to decrypt message: %v"}`, err)
		return
	}

	// Prepare the response with the decrypted message
	response := DecryptedResponse{
		Message: string(plaintextMessage),
	}
	responseBody, _ := json.Marshal(response)

	// Print the response
	fmt.Println(string(responseBody))
}

// AES-GCM decryption
func decryptMessageWithAESGCM(key []byte, ciphertext []byte, iv []byte, tag []byte) ([]byte, error) {
	ivSize := 12

	// Create a new AES cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("failed to create AES cipher: %w", err)
	}

	// Use GCM mode for decryption
	gcm, err := cipher.NewGCMWithNonceSize(block, ivSize)
	if err != nil {
		return nil, fmt.Errorf("failed to create GCM cipher: %w", err)
	}

	// Reconstruct the full ciphertext (ciphertext + tag)
	fullCiphertext := append(ciphertext, tag...)

	// Decrypt the message
	plaintext, err := gcm.Open(nil, iv, fullCiphertext, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to decrypt message: %w", err)
	}

	return plaintext, nil
}
