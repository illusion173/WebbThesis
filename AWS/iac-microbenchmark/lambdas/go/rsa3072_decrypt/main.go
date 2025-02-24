// This file is autogenerated for directory: rsa3072_decrypt
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

type RSA3072DecryptRequest struct {
	Ciphertext   string `json:"ciphertext"`
	Iv           string `json:"iv"`
	EncryptedKey string `json:"encrypted_aes_key"`
}

type RSA3072DecryptResponse struct {
	Message string `json:"message"`
}

func handler(ctx context.Context, request events.LambdaFunctionURLRequest) (events.LambdaFunctionURLResponse, error) {
	rsaKmsKeyId := os.Getenv("RSA3072_KMS_KEY_ARN")
	if rsaKmsKeyId == "" {
		return events.LambdaFunctionURLResponse{
			StatusCode: 400,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
			},
			Body: "RSA 3072 KMS key ARN not set",
		}, nil
	}

	// Parse the request body
	var reqBody RSA3072DecryptRequest
	err := json.Unmarshal([]byte(request.Body), &reqBody)
	if err != nil {
		return events.LambdaFunctionURLResponse{
			StatusCode: 400,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: "Invalid Request Body, missing fields.",
		}, nil
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return events.LambdaFunctionURLResponse{
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
	message, err := awsKmsRsaDecrypt(ctx, kmsClient, rsaKmsKeyId, reqBody)
	if err != nil {
		return events.LambdaFunctionURLResponse{
			StatusCode: 500,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: fmt.Sprintf("Error decrypting message: %v", err),
		}, nil
	}

	// Build the response
	responseBody, err := json.Marshal(RSA3072DecryptResponse{Message: message})
	if err != nil {
		return events.LambdaFunctionURLResponse{
			StatusCode: 500,
			Headers: map[string]string{
				"Access-Control-Allow-Origin": "*",
				"Content-Type":                "application/json",
			},
			Body: fmt.Sprintf("Error marshalling response: %v", err),
		}, nil
	}

	return events.LambdaFunctionURLResponse{
		StatusCode: 200,
		Headers: map[string]string{
			"Access-Control-Allow-Origin": "*",
			"Content-Type":                "application/json",
		},
		Body: string(responseBody),
	}, nil
}

func awsKmsRsaDecrypt(ctx context.Context, kmsClient *kms.Client, keyID string, request RSA3072DecryptRequest) (string, error) {
	// Decode the base64-encoded AES key, IV, and ciphertext
	encryptedAESKey, err := base64.StdEncoding.DecodeString(request.EncryptedKey)
	if err != nil {
		return "", fmt.Errorf("failed to decode encrypted key: %v", err)
	}

	iv, err := base64.StdEncoding.DecodeString(request.Iv)
	if err != nil {
		return "", fmt.Errorf("failed to decode IV: %v", err)
	}

	ciphertext, err := base64.StdEncoding.DecodeString(request.Ciphertext)
	if err != nil {
		return "", fmt.Errorf("failed to decode ciphertext: %v", err)
	}

	// Decrypt the AES key using KMS
	kmsDecryptOutput, err := kmsClient.Decrypt(ctx, &kms.DecryptInput{
		KeyId:               aws.String(keyID),
		CiphertextBlob:      encryptedAESKey,
		EncryptionAlgorithm: types.EncryptionAlgorithmSpecRsaesOaepSha256,
	})
	if err != nil {
		return "", fmt.Errorf("KMS decryption failed: %v", err)
	}

	decryptedAESKey := kmsDecryptOutput.Plaintext

	// Decrypt the message using AES-CTR
	block, err := aes.NewCipher(decryptedAESKey)
	if err != nil {
		return "", fmt.Errorf("failed to create AES cipher: %v", err)
	}

	stream := cipher.NewCTR(block, iv)
	decryptedMessage := make([]byte, len(ciphertext))
	stream.XORKeyStream(decryptedMessage, ciphertext)

	// Convert decrypted message to string
	return string(decryptedMessage), nil
}

func main() {
	lambda.Start(handler)
}
