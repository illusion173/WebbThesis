#!/usr/bin/env node

import { KMSClient, GenerateMacCommand } from '@aws-sdk/client-kms';
import * as process from 'process';

// Initialize the AWS KMS client
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});// Define the signing algorithm

const SIGN_ALGORITHM = 'HMAC_SHA_256';

async function main(): Promise<void> {
  try {
    // Get the JSON input from command line arguments
    const requestJsonRaw: string = process.argv[2];

    // Parse the JSON input
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message from the parsed JSON
    const message: string = requestJson["message"];

    // Retrieve the KMS key ARN from environment variables
    const shaKmsKeyId = process.env['SHA256_KMS_KEY_ARN'];

    // Check if the KMS key ARN is provided
    if (!shaKmsKeyId) {
      throw new Error("SHA256_KMS_KEY_ARN environment variable is not set");
    }

    // Convert the message to bytes
    const messageBytes = Buffer.from(message, 'utf-8');

    // Create the command to generate the HMAC
    const command = new GenerateMacCommand({
      KeyId: shaKmsKeyId,
      Message: messageBytes,
      MacAlgorithm: SIGN_ALGORITHM,
    });

    // Use KMS to generate HMAC of the message
    const response = await kmsClient.send(command);

    // Base64 encode the signature for output
    const signature = Buffer.from(response.Mac as Uint8Array).toString('base64');

    // Create a result object to return the signature
    const resultDict = {
      "signature": signature
    };

    // Output the result as a JSON string
    console.log(JSON.stringify(resultDict));
  } catch (error) {
    // Handle and log any errors that occur
    console.error("Error:", error);
  }
}

// Execute the main function
main();
