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

// Struct to parse the input JSON message
type MessageStruct struct {
	Message string `json:"message"`
}

// Struct to structure the output response JSON
type ResponseStruct struct {
	Signature string `json:"signature,omitempty"`
	Error     string `json:"error,omitempty"`
}

func main() {
	// Retrieve JSON input from command-line argument
	requestJSONRaw := os.Args[1]
	var messageStruct MessageStruct

	// Parse the JSON input
	if err := json.Unmarshal([]byte(requestJSONRaw), &messageStruct); err != nil || messageStruct.Message == "" {
		fmt.Println(`{"error": "Invalid input: missing or malformed message"}`)
		return
	}

	// Get the KMS key ARN from environment variable
	shaKmsKeyID := os.Getenv("SHA384_KMS_KEY_ARN")
	if shaKmsKeyID == "" {
		fmt.Println(`{"error": "KMS key ARN environment variable not set"}`)
		return
	}

	// Convert the message to bytes
	messageBytes := []byte(messageStruct.Message)

	context := context.Background()
	// Load AWS configuration
	cfg, err := config.LoadDefaultConfig(context)
	if err != nil {
		fmt.Println(`{"error": "Failed to load AWS config"}`)
		return
	}

	// Create a new KMS client
	kmsClient := kms.NewFromConfig(cfg)

	// Sign the message using KMS
	signature, err := kmsSignMessage(context, kmsClient, shaKmsKeyID, messageBytes)
	if err != nil {
		fmt.Printf(`{"error": "Error signing message: %v"}`, err)
		return
	}

	// Create a JSON response
	response := ResponseStruct{Signature: signature}
	responseJSON, _ := json.Marshal(response)
	fmt.Println(string(responseJSON))
}

// Function to sign a message using AWS KMS
func kmsSignMessage(ctx context.Context, kmsClient *kms.Client, keyID string, message []byte) (string, error) {
	// Call KMS to generate MAC (HMAC) signature
	macOutput, err := kmsClient.GenerateMac(ctx, &kms.GenerateMacInput{
		KeyId:        aws.String(keyID),
		Message:      message,
		MacAlgorithm: types.MacAlgorithmSpecHmacSha384,
	})
	if err != nil {
		return "", fmt.Errorf("failed to generate MAC: %w", err)
	}

	// Base64 encode the generated MAC
	if macOutput.Mac == nil {
		return "", fmt.Errorf("no MAC hash returned")
	}
	return base64.StdEncoding.EncodeToString(macOutput.Mac), nil
}
