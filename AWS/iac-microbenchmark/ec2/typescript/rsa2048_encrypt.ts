#!/usr/bin/env node

import { KMSClient, EncryptCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as crypto from 'crypto';
import * as base64 from 'base64-js';

// Initialize the AWS KMS client with the specified region
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});

async function main(): Promise<void> {
  try {
    // Get the JSON input from command line argument
    const requestJsonRaw: string = process.argv[2];

    // Parse the JSON input
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message from the input payload
    const message: string = requestJson.message;

    // Get the KMS key ID from environment variables
    const rsaKmsKeyId = process.env['RSA2048_KMS_KEY_ID'];

    if (!rsaKmsKeyId) {
      throw new Error("RSA2048_KMS_KEY_ID environment variable is not set");
    }

    // Generate a random AES key and IV
    const aesKey = crypto.randomBytes(32); // 256 bits for AES-256
    const iv = crypto.randomBytes(16); // 128 bits for AES IV

    // Encrypt the data using AES in CTR mode
    const cipher = crypto.createCipheriv('aes-256-ctr', aesKey, iv);
    const ciphertext = Buffer.concat([cipher.update(message, 'utf8'), cipher.final()]);

    // Encrypt the AES key using KMS
    const encryptCommand = new EncryptCommand({
      KeyId: rsaKmsKeyId,
      Plaintext: aesKey,
      EncryptionAlgorithm: 'RSAES_OAEP_SHA_256' // Use the specified encryption algorithm
    });

    const response = await kmsClient.send(encryptCommand);
    const encryptedAesKey = response.CiphertextBlob;

    // Return the results
    const result = {
      iv: base64.fromByteArray(iv),
      ciphertext: base64.fromByteArray(ciphertext),
      encrypted_aes_key: base64.fromByteArray(encryptedAesKey as Uint8Array)
    };

    console.log(JSON.stringify(result));
  } catch (error) {
    console.error("Error:", error);
  }
}

// Execute the main function
main();
