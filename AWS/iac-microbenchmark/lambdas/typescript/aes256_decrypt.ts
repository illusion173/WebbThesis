import { KMSClient, DecryptCommand } from "@aws-sdk/client-kms";
import { createDecipheriv } from "crypto";
import { Context } from 'aws-lambda';

// handler for AWS Lambda
export const handler = async (event: any, context: Context): Promise<any> => {

  // Initialize the KMS client
  const kmsClient = new KMSClient({ region: 'us-east-1' });

  // Get the KMS-encrypted key, IV, authentication tag, and encrypted message from the event body
  const body = event.body ? JSON.parse(event.body) : {};
  const { encrypted_data_key, iv, tag, encrypted_message } = body;

  if (!encrypted_data_key || !iv || !tag || !encrypted_message) {
    return {
      statusCode: 400,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ error: "Missing required parameters" }),
    };
  }

  // Decrypt the encrypted data key using KMS
  const decryptCommand = new DecryptCommand({
    CiphertextBlob: Buffer.from(encrypted_data_key, "base64"),
  });

  try {
    const decryptResponse = await kmsClient.send(decryptCommand);
    const plaintextDataKey = decryptResponse.Plaintext as Uint8Array;

    // Convert the IV and tag back from base64
    const ivBuffer = Buffer.from(iv, "base64");
    const tagBuffer = Buffer.from(tag, "base64");
    const encryptedMessageBuffer = Buffer.from(encrypted_message, "base64");

    // Decrypt the message using AES-GCM
    const decipher = createDecipheriv("aes-256-gcm", plaintextDataKey, ivBuffer);
    decipher.setAuthTag(tagBuffer);

    const decryptedMessage = Buffer.concat([
      decipher.update(encryptedMessageBuffer),
      decipher.final(),
    ]).toString("utf-8");

    // Return the decrypted message
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        decrypted_message: decryptedMessage,
      }),
    };

  } catch (error) {
    console.error('Error decrypting message:', error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ error: 'An error occurred during the decryption process' }),
    };
  }
};
