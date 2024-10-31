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

type RSA4096Request struct {
	Message string `json:"message"`
}

type RSA4096Response struct {
	Ciphertext   string `json:"ciphertext"`
	Iv           string `json:"iv"`
	EncryptedKey string `json:"encrypted_key"`
}

func main() {
	// Check if an argument is provided
	if len(os.Args) < 2 {
		fmt.Println("Error: No input provided. Please provide a JSON string as input.")
		return
	}

	// Get the JSON input from command line argument
	requestJSONRaw := os.Args[1]

	var reqBody RSA4096Request
	err := json.Unmarshal([]byte(requestJSONRaw), &reqBody)
	if err != nil {
		fmt.Printf("Error unmarshalling request body: %v\n", err)
		return
	}

	rsaKmsKeyId := os.Getenv("RSA4096_KMS_KEY_ARN")
	if rsaKmsKeyId == "" {
		fmt.Println("Error: RSA 4096 KMS key ARN not set")
		return
	}

	// Load the AWS configuration
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		fmt.Printf("Error loading AWS config: %v\n", err)
		return
	}

	kmsClient := kms.NewFromConfig(cfg)

	// Encrypt the message
	rsaResponse, err := awsKmsRsaEncrypt(context.TODO(), kmsClient, rsaKmsKeyId, reqBody.Message)
	if err != nil {
		fmt.Printf("Error encrypting message: %v\n", err)
		return
	}

	// Build the response
	responseBody, err := json.Marshal(rsaResponse)
	if err != nil {
		fmt.Printf("Error marshalling response: %v\n", err)
		return
	}

	fmt.Println(string(responseBody))
}

func awsKmsRsaEncrypt(ctx context.Context, kmsClient *kms.Client, keyID, message string) (*RSA4096Response, error) {
	// Generate AES key and IV
	aesKey := make([]byte, 32) // AES-256 key size
	iv := make([]byte, aes.BlockSize)

	_, err := io.ReadFull(rand.Reader, aesKey)
	if err != nil {
		return nil, fmt.Errorf("failed to generate AES key: %v", err)
	}
	_, err = io.ReadFull(rand.Reader, iv)
	if err != nil {
		return nil, fmt.Errorf("failed to generate IV: %v", err)
	}

	// Encrypt the message using AES-CTR
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, fmt.Errorf("failed to create AES cipher: %v", err)
	}

	stream := cipher.NewCTR(block, iv)
	ciphertext := make([]byte, len(message))
	stream.XORKeyStream(ciphertext, []byte(message))

	// Encrypt the AES key using KMS
	kmsEncryptOutput, err := kmsClient.Encrypt(ctx, &kms.EncryptInput{
		KeyId:               aws.String(keyID),
		Plaintext:           aesKey,
		EncryptionAlgorithm: types.EncryptionAlgorithmSpecRsaesOaepSha256,
	})
	if err != nil {
		return nil, fmt.Errorf("KMS encryption failed: %v", err)
	}

	// Base64 encode the ciphertext, IV, and encrypted AES key
	encodedCiphertext := base64.StdEncoding.EncodeToString(ciphertext)
	encodedIV := base64.StdEncoding.EncodeToString(iv)
	encodedEncryptedAESKey := base64.StdEncoding.EncodeToString(kmsEncryptOutput.CiphertextBlob)

	// Build the response
	return &RSA4096Response{
		Ciphertext:   encodedCiphertext,
		Iv:           encodedIV,
		EncryptedKey: encodedEncryptedAESKey,
	}, nil
}
