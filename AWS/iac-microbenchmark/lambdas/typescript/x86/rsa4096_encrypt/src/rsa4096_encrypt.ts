import { KMSClient, EncryptCommand } from "@aws-sdk/client-kms";
import * as crypto from "crypto";
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize KMS Client
const kmsClient = new KMSClient({});

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {

  // Get the KMS key ID from environment variables 
  const rsaKmsKeyId = process.env.RSA4096_KMS_KEY_ARN;

  if (!rsaKmsKeyId) {
    return {
      statusCode: 400,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ message: "KMS Key ID not provided" }),
    };
  }

  try {
    // Generate a random AES key (256 bits)
    const aesKey = crypto.randomBytes(32);

    // Generate a random IV (16 bytes)
    const iv = crypto.randomBytes(16);

    // Create AES-CTR cipher
    const cipher = crypto.createCipheriv('aes-256-ctr', aesKey, iv);

    // Encrypt the message from the event
    const plaintext = Buffer.from(event.body ? JSON.parse(event.body).message : '', 'utf-8');
    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);

    // Encrypt the AES key using KMS
    const encryptCommand = new EncryptCommand({
      KeyId: rsaKmsKeyId,
      Plaintext: aesKey,
      EncryptionAlgorithm: "RSAES_OAEP_SHA_256",
    });

    const response = await kmsClient.send(encryptCommand);
    const encryptedAesKey = response.CiphertextBlob;

    // Return encrypted data, IV, and AES key
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        iv: iv.toString('base64'),
        ciphertext: ciphertext.toString('base64'),
        encryptedAesKey: Buffer.from(encryptedAesKey!).toString('base64'),
      }),
    };
  } catch (error) {
    console.error("Error encrypting data: ", error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ message: "Encryption failed" }),
    };
  }
};
