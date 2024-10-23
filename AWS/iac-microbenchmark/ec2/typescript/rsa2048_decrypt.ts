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
    // Get the JSON input from command line argument
    const requestJsonRaw: string = process.argv[2];

    // Parse the JSON input
    const requestJson = JSON.parse(requestJsonRaw);

    // Get the KMS key ID from environment variables
    const rsaKmsKeyId = process.env['RSA2048_KMS_KEY_ID'];

    if (!rsaKmsKeyId) {
      throw new Error("RSA2048_KMS_KEY_ID environment variable is not set");
    }

    // Get the data from the input payload
    const encryptedAesKeyB64 = requestJson.encrypted_aes_key;
    const ivB64 = requestJson.iv;
    const ciphertextB64 = requestJson.ciphertext;

    // Decode base64 values
    const encryptedAesKey = base64.toByteArray(encryptedAesKeyB64);
    const iv = base64.toByteArray(ivB64);
    const ciphertext = base64.toByteArray(ciphertextB64);

    // Decrypt the AES key using KMS
    const decryptCommand = new DecryptCommand({
      CiphertextBlob: encryptedAesKey,
      KeyId: rsaKmsKeyId,
      EncryptionAlgorithm: 'RSAES_OAEP_SHA_256' // Specify the encryption algorithm
    });

    const response = await kmsClient.send(decryptCommand);
    const aesKey = response.Plaintext as Uint8Array;

    // Decrypt the data using AES in CTR mode
    const decipher = crypto.createDecipheriv('aes-256-ctr', aesKey, iv);
    const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);

    // Return the plaintext as a JSON response
    const result = {
      plaintext: plaintext.toString('utf-8')
    };

    console.log(JSON.stringify(result));
  } catch (error) {
    console.error("Error:", error);
  }
}

// Execute the main function
main();
