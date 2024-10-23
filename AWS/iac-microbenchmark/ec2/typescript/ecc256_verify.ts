#!/usr/bin/env node
import { KMSClient, VerifyCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as base64 from 'base64-js';

// Initialize the AWS KMS client with the specified region
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});

async function main(): Promise<void> {
  try {
    // Get the JSON input from command line arguments
    const requestJsonRaw: string = process.argv[2];

    // Parse the JSON input
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message and signature from the parsed JSON
    const message: string = requestJson.get('message');
    const signatureB64: string = requestJson.get('signature');

    // Decode the base64-encoded signature
    const signature = base64.toByteArray(signatureB64);

    // Retrieve the KMS key ARN from environment variables
    const eccKmsKeyId = process.env['ECC256_KMS_KEY_ARN'];

    if (!eccKmsKeyId) {
      throw new Error("ECC256_KMS_KEY_ARN environment variable is not set");
    }

    // Verify the signature using KMS
    const verifyCommand = new VerifyCommand({
      KeyId: eccKmsKeyId,
      Message: Buffer.from(message, 'utf-8'),
      MessageType: 'RAW',
      Signature: signature,
      SigningAlgorithm: 'ECDSA_SHA_256' // Use 'ECDSA_SHA_384' for P-384
    });

    const response = await kmsClient.send(verifyCommand);

    // Output the result of the verification
    console.log(JSON.stringify({ verified: response.SignatureValid }));
  } catch (error) {
    // Handle and log any errors that occur
    console.error("Error:", error);
  }
}

// Execute the main function
main();
