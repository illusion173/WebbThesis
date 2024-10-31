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

// ECC384Request represents the input message
type ECC384Request struct {
	Message string `json:"message"`
}

// ECC384Response represents the signed response
type ECC384Response struct {
	Signature string `json:"signature"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println(`{"error": "Missing JSON input"}`)
		return
	}

	// Get the JSON input from command line argument
	requestJSONRaw := os.Args[1]

	var messageStruct ECC384Request
	if err := json.Unmarshal([]byte(requestJSONRaw), &messageStruct); err != nil || messageStruct.Message == "" {
		fmt.Println(`{"error": "Invalid request body, missing message"}`)
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
	eccKmsKeyID := os.Getenv("ECC384_KMS_KEY_ARN")
	if eccKmsKeyID == "" {
		fmt.Println(`{"error": "ECC 384 KMS key ARN not set"}`)
		return
	}

	// Call the function to sign the message using KMS
	signatureResponse, err := kmsClientSignMessage(ctx, kmsClient, eccKmsKeyID, messageStruct.Message)
	if err != nil {
		fmt.Printf(`{"error": "Error signing message: %v"}`, err)
		return
	}

	// Prepare the response body
	responseBody, _ := json.Marshal(signatureResponse)

	// Print the response
	fmt.Println(string(responseBody))
}

// kmsClientSignMessage calls KMS to sign the message using ECC384
func kmsClientSignMessage(ctx context.Context, kmsClient *kms.Client, keyID string, message string) (*ECC384Response, error) {
	// Convert the message to a Blob
	messageBlob := []byte(message)

	// Call KMS to sign the message
	signOutput, err := kmsClient.Sign(ctx, &kms.SignInput{
		KeyId:            aws.String(keyID),
		Message:          messageBlob,
		MessageType:      types.MessageTypeRaw,
		SigningAlgorithm: types.SigningAlgorithmSpecEcdsaSha384, // Use EcdsaSha384 for ECC384
	})
	if err != nil {
		return nil, fmt.Errorf("failed to sign message: %w", err)
	}

	// Get the signature from the response
	if signOutput.Signature == nil {
		return nil, fmt.Errorf("no signature returned from KMS")
	}

	// Encode the signature in Base64
	signatureB64 := base64.StdEncoding.EncodeToString(signOutput.Signature)

	// Prepare the response
	return &ECC384Response{
		Signature: signatureB64,
	}, nil
}
