#!/usr/bin/env node
import { KMSClient, DecryptCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as crypto from 'crypto';
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

    // Extract the encrypted data key, IV, tag, and encrypted message from the parsed JSON
    const encryptedDataKey = base64.toByteArray(requestJson.encrypted_data_key);
    const ciphertext = base64.toByteArray(requestJson.encrypted_message);
    const iv = base64.toByteArray(requestJson.iv);
    const tag = base64.toByteArray(requestJson.tag);

    // Decrypt the data key using KMS
    const decryptCommand = new DecryptCommand({
      CiphertextBlob: encryptedDataKey
    });

    const response = await kmsClient.send(decryptCommand);
    const plaintextDataKey = response.Plaintext as Uint8Array;

    // Initialize decryption using AES-GCM
    const cipher = crypto.createDecipheriv('aes-256-gcm', plaintextDataKey, iv);
    cipher.setAuthTag(tag);

    // Decrypt the message
    const plaintextMessage = Buffer.concat([
      cipher.update(ciphertext),
      cipher.final()
    ]);

    // Prepare the decrypted message for output
    const decryptMessage = {
      Message: plaintextMessage.toString('utf-8') // Convert to string
    };

    // Output the decrypted message as a JSON string
    console.log(JSON.stringify(decryptMessage));
  } catch (error) {
    // Handle and log any errors that occur
    console.error("Error:", error);
  }
}

// Execute the main function
main();
