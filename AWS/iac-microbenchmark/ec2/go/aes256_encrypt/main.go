// main.go
package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kms"
	"github.com/aws/aws-sdk-go-v2/service/kms/types"
)

// Struct to parse the input JSON message
type MessageStruct struct {
	Message string `json:"message"`
}

// Struct for the encrypted response output
type EncryptedResponse struct {
	Ciphertext   string `json:"ciphertext"`
	EncryptedAesKey string `json:"encrypted_aes_key"`
	IV           string `json:"iv"`
	Tag          string `json:"tag"`
	Error        string `json:"error,omitempty"`
}

func main() {
	// Read JSON input from command-line argument
	requestJSONRaw := os.Args[1]
	var messageStruct MessageStruct

	// Parse the JSON input
	if err := json.Unmarshal([]byte(requestJSONRaw), &messageStruct); err != nil || messageStruct.Message == "" {
		fmt.Println(`{"error": "Invalid input: missing or malformed message"}`)
		return
	}

	// Retrieve the KMS key ARN from the environment
	kmsKeyID := os.Getenv("AES_KMS_KEY_ARN")
	if kmsKeyID == "" {
		fmt.Println(`{"error": "KMS key ARN environment variable not set"}`)
		return
	}

	context := context.Background()
	// Load AWS configuration
	cfg, err := config.LoadDefaultConfig(context)
	if err != nil {
		fmt.Println(`{"error": "Failed to load AWS config"}`)
		return
	}

	// Create a KMS client
	kmsClient := kms.NewFromConfig(cfg)

	// Generate a data key using KMS
	dataKeyOutput, err := kmsClient.GenerateDataKey(context, &kms.GenerateDataKeyInput{
		KeyId:   aws.String(kmsKeyID),
		KeySpec: types.DataKeySpecAes256,
	})
	if err != nil {
		fmt.Printf(`{"error": "Failed to generate data key: %v"}`, err)
		return
	}

	// Extract plaintext and encrypted data key
	plaintextDataKey := dataKeyOutput.Plaintext
	encryptedDataKey := dataKeyOutput.CiphertextBlob

	// Encrypt the message using AES-GCM
	ciphertext, iv, tag, err := encryptMessageWithAESGCM(plaintextDataKey, []byte(messageStruct.Message))
	if err != nil {
		fmt.Printf(`{"error": "Failed to encrypt message: %v"}`, err)
		return
	}

	// Prepare the response
	response := EncryptedResponse{
		Ciphertext:   base64.StdEncoding.EncodeToString(ciphertext),
		EncryptedAesKey: base64.StdEncoding.EncodeToString(encryptedDataKey),
		IV:           base64.StdEncoding.EncodeToString(iv),
		Tag:          base64.StdEncoding.EncodeToString(tag),
	}
	responseJSON, _ := json.Marshal(response)
	fmt.Println(string(responseJSON))
}

// AES-GCM encryption function
func encryptMessageWithAESGCM(key []byte, message []byte) ([]byte, []byte, []byte, error) {
	ivSize := 12

	// Create a new AES cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to create AES cipher: %w", err)
	}

	// Use GCM mode for encryption with a specified IV size
	gcm, err := cipher.NewGCMWithNonceSize(block, ivSize)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to create GCM cipher: %w", err)
	}

	// Generate a random IV
	iv := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil, fmt.Errorf("failed to generate IV: %w", err)
	}

	// Encrypt the message using AES-GCM
	ciphertext := gcm.Seal(nil, iv, message, nil)
	tag := ciphertext[len(ciphertext)-gcm.Overhead():]
	ciphertext = ciphertext[:len(ciphertext)-gcm.Overhead()]

	return ciphertext, iv, tag, nil
}
