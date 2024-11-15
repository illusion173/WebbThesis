#!/usr/bin/env node

import { KMSClient, GenerateDataKeyCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as crypto from 'crypto';
import * as base64 from 'base64-js';

// Initialize the AWS KMS client with the specified region
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});

async function main(): Promise<void> {
  try {
    // Get the KMS key ARN from environment variables
    const kmsKeyId = process.env['AES_KMS_KEY_ARN'];

    // Check if the KMS key ARN is provided
    if (!kmsKeyId) {
      throw new Error("AES_KMS_KEY_ARN environment variable is not set");
    }

    // Get the JSON input from command line arguments
    const requestJsonRaw: string = process.argv[2];

    // Parse the JSON input
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message from the parsed JSON
    const message: string = requestJson["message"];

    // Create a new data key for AES-256-GCM encryption
    const generateDataKeyCommand = new GenerateDataKeyCommand({
      KeyId: kmsKeyId,
      KeySpec: 'AES_256',
    });

    const response = await kmsClient.send(generateDataKeyCommand);

    const plaintextDataKey = response.Plaintext as Uint8Array; // The plaintext data key
    const encryptedDataKey = response.CiphertextBlob as Uint8Array; // The encrypted data key

    const iv = crypto.randomBytes(12); // 12 bytes for AES-GCM IV

    // Create a cipher using AES-GCM
    const cipher = crypto.createCipheriv('aes-256-gcm', plaintextDataKey, iv);

    // Encrypt the message (no padding required in AES-GCM)
    const ciphertext = Buffer.concat([
      cipher.update(Buffer.from(message, 'utf-8')),
      cipher.final()
    ]);

    // Get the authentication tag
    const tag = cipher.getAuthTag();

    // Prepare the result
    const encryptResult = {
      encrypted_data_key: base64.fromByteArray(encryptedDataKey),
      iv: base64.fromByteArray(iv),
      tag: base64.fromByteArray(tag),
      encrypted_message: base64.fromByteArray(ciphertext)
    };

    // Output the result as a JSON string
    console.log(JSON.stringify(encryptResult));
  } catch (error) {
    // Handle and log any errors that occur
    console.error("Error:", error);
  }
}

// Execute the main function
main();
