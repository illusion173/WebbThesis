// main.go
package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kms"
	"github.com/aws/aws-sdk-go-v2/service/kms/types"
)

// ECC256Request represents the input message and signature
type ECC256Request struct {
	Message   string `json:"message"`
	Signature string `json:"signature"`
}

// ECC256Response represents the validation response
type ECC256Response struct {
	Valid bool `json:"valid"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println(`{"error": "Missing JSON input"}`)
		return
	}

	// Get the JSON input from command line argument
	requestJSONRaw := os.Args[1]

	var messageStruct ECC256Request
	if err := json.Unmarshal([]byte(requestJSONRaw), &messageStruct); err != nil || messageStruct.Message == "" || messageStruct.Signature == "" {
		fmt.Println(`{"error": "Invalid request body, missing message or signature"}`)
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

	// Initialize KMS client
	kmsClient := kms.NewFromConfig(cfg)

	// Get the KMS key ARN from environment variables
	eccKmsKeyID := os.Getenv("ECC256_KMS_KEY_ARN")
	if eccKmsKeyID == "" {
		fmt.Println(`{"error": "ECC 256 KMS key ARN not set"}`)
		return
	}

	// Call the function to verify the signature using KMS
	verificationResponse, err := kmsClientVerifyMessage(ctx, kmsClient, eccKmsKeyID, messageStruct.Message, messageStruct.Signature)
	if err != nil {
		fmt.Printf(`{"error": "Error verifying message: %v"}`, err)
		return
	}

	// Prepare the response body
	responseBody, _ := json.Marshal(verificationResponse)

	// Print the response
	fmt.Println(string(responseBody))
}

// kmsClientVerifyMessage verifies the message signature using ECC256 and AWS KMS
func kmsClientVerifyMessage(ctx context.Context, kmsClient *kms.Client, keyID string, message string, signatureB64 string) (*ECC256Response, error) {
	// Decode the base64-encoded signature
	signature, err := base64.StdEncoding.DecodeString(signatureB64)
	if err != nil {
		return nil, fmt.Errorf("failed to decode signature: %w", err)
	}

	// Perform the verification with KMS
	verifyOutput, err := kmsClient.Verify(ctx, &kms.VerifyInput{
		KeyId:            aws.String(keyID),
		Message:          []byte(message),
		MessageType:      types.MessageTypeRaw,
		Signature:        signature,
		SigningAlgorithm: types.SigningAlgorithmSpecEcdsaSha256,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to verify message: %w", err)
	}

	// Prepare the response
	return &ECC256Response{
		Valid: verifyOutput.SignatureValid,
	}, nil
}
