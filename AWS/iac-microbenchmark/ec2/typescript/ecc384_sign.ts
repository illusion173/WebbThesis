#!/usr/bin/env node
import { KMSClient, SignCommand } from '@aws-sdk/client-kms';
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

    // Extract the message from the parsed JSON
    const message: string = requestJson.get('message');

    // Retrieve the KMS key ARN from environment variables
    const eccKmsKeyId = process.env['ECC384_KMS_KEY_ARN'];

    if (!eccKmsKeyId) {
      throw new Error("ECC384_KMS_KEY_ARN environment variable is not set");
    }

    // Sign the message using KMS
    const signCommand = new SignCommand({
      KeyId: eccKmsKeyId,
      Message: Buffer.from(message, 'utf-8'),
      MessageType: 'RAW',
      SigningAlgorithm: 'ECDSA_SHA_384' // Use 'ECDSA_SHA_384' for P-384
    });

    const response = await kmsClient.send(signCommand);
    const signature = response.Signature as Uint8Array;

    // Encode the signature to base64 for easier transport
    const signatureB64 = base64.fromByteArray(signature);

    // Output the result as a JSON string
    console.log(JSON.stringify({ signature: signatureB64 }));
  } catch (error) {
    // Handle and log any errors that occur
    console.error("Error:", error);
  }
}

// Execute the main function
main();
