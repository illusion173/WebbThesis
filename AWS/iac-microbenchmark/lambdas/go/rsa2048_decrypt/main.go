// This file is autogenerated for directory: rsa2048_decrypt
package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kms"
	"github.com/aws/aws-sdk-go-v2/service/kms/types"
)

type RSA2048DecryptRequest struct {
	Ciphertext   string `json:"ciphertext"`
	Iv           string `json:"iv"`
	EncryptedKey string `json:"encrypted_key"`
}

type RSA2048DecryptResponse struct {
	Message string `json:"message"`
}

func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	rsaKmsKeyId := os.Getenv("RSA2048_KMS_KEY_ARN")
	if rsaKmsKeyId == "" {
		return events.APIGatewayProxyResponse{
			StatusCode: 400,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
			},
			Body: "RSA 2048 KMS key ARN not set",
		}, nil
	}

	// Parse the request body
	var reqBody RSA2048DecryptRequest
	err := json.Unmarshal([]byte(request.Body), &reqBody)
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 400,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: "Invalid Request Body, missing data.",
		}, nil
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 500,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: fmt.Sprintf("Error loading AWS config: %v", err),
		}, nil
	}

	kmsClient := kms.NewFromConfig(cfg)

	// Decrypt the message
	decryptedMessage, err := awsKmsRsaDecrypt(ctx, kmsClient, rsaKmsKeyId, &reqBody)
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 500,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: fmt.Sprintf("Error decrypting message: %v", err),
		}, nil
	}

	// Build the response
	responseBody, err := json.Marshal(RSA2048DecryptResponse{
		Message: decryptedMessage,
	})
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 500,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: fmt.Sprintf("Error marshalling response: %v", err),
		}, nil
	}

	return events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers: map[string]string{
			"Access-Control-Allow-Origin": "*",
			"Content-Type":                "application/json",
		},
		Body: string(responseBody),
	}, nil
}

func awsKmsRsaDecrypt(ctx context.Context, kmsClient *kms.Client, keyID string, request *RSA2048DecryptRequest) (string, error) {
	// Step 1: Decode the base64-encoded AES key, IV, and ciphertext
	encryptedAESKey, err := base64.StdEncoding.DecodeString(request.EncryptedKey)
	if err != nil {
		return "", fmt.Errorf("failed to decode encrypted_key: %v", err)
	}

	iv, err := base64.StdEncoding.DecodeString(request.Iv)
	if err != nil {
		return "", fmt.Errorf("failed to decode IV: %v", err)
	}

	ciphertext, err := base64.StdEncoding.DecodeString(request.Ciphertext)
	if err != nil {
		return "", fmt.Errorf("failed to decode ciphertext: %v", err)
	}

	// Step 2: Decrypt the AES key using AWS KMS
	kmsDecryptOutput, err := kmsClient.Decrypt(ctx, &kms.DecryptInput{
		KeyId:               aws.String(keyID),
		CiphertextBlob:      encryptedAESKey,
		EncryptionAlgorithm: types.EncryptionAlgorithmSpecRsaesOaepSha256,
	})
	if err != nil {
		return "", fmt.Errorf("KMS decryption failed: %v", err)
	}

	decryptedAESKey := kmsDecryptOutput.Plaintext

	// Step 3: Decrypt the message using AES-256-CTR
	block, err := aes.NewCipher(decryptedAESKey)
	if err != nil {
		return "", fmt.Errorf("failed to create AES cipher: %v", err)
	}

	stream := cipher.NewCTR(block, iv)
	decryptedMessage := make([]byte, len(ciphertext))
	stream.XORKeyStream(decryptedMessage, ciphertext)

	// Convert decrypted message to string
	decryptedMessageStr := string(decryptedMessage)

	return decryptedMessageStr, nil
}

func main() {
	lambda.Start(handler)
}