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
	// Get the JSON input from command line argument
	requestJSONRaw := os.Args[1]

	var requestJSON map[string]string
	if err := json.Unmarshal([]byte(requestJSONRaw), &requestJSON); err != nil {
		fmt.Printf("Error unmarshalling JSON: %v\n", err)
		return
	}

	message, ok := requestJSON["message"]
	if !ok {
		fmt.Println("Error: message field is required")
		return
	}

	shaKmsKeyID := os.Getenv("SHA384_KMS_KEY_ARN")
	if shaKmsKeyID == "" {
		fmt.Println("Error: SHA384_KMS_KEY_ARN environment variable is not set")
		return
	}

	context := context.Background()
	// Load the default AWS configuration
	cfg, err := config.LoadDefaultConfig(context, config.WithRegion("us-east-1"))
	if err != nil {
		fmt.Printf("unable to load SDK config, %v\n", err)
		return
	}

	// Create a new KMS client
	kmsClient := kms.NewFromConfig(cfg)

	// Convert the message to bytes
	messageBytes := []byte(message)

	// Use KMS to generate HMAC for the message
	input := &kms.GenerateMacInput{
		KeyId:        aws.String(shaKmsKeyID),
		Message:      messageBytes,
		MacAlgorithm: types.MacAlgorithmSpecHmacSha384,
	}

	response, err := kmsClient.GenerateMac(context, input)
	if err != nil {
		fmt.Printf("Error generating MAC: %v\n", err)
		return
	}

	// Base64 encode the signature for output
	signature := base64.StdEncoding.EncodeToString(response.Mac)

	// Prepare the result
	resultDict := map[string]string{
		"signature": signature,
	}

	resultJSON, err := json.Marshal(resultDict)
	if err != nil {
		fmt.Printf("Error marshalling result to JSON: %v\n", err)
		return
	}

	fmt.Println(string(resultJSON))
}
