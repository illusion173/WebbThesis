
import { KMSClient, DecryptCommand } from "@aws-sdk/client-kms";
import * as crypto from "crypto";
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize KMS Client
const kmsClient = new KMSClient({});

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {

  // Get the KMS key ID from environment variables
  const rsaKmsKeyId = process.env.RSA3072_KMS_KEY_ID;

  if (!rsaKmsKeyId) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: "KMS Key ID not provided" }),
    };
  }

  // Get encrypted data from the event
  const encryptedAesKey = Buffer.from(event.body ? JSON.parse(event.body).encrypted_aes_key : '', 'base64');
  const iv = Buffer.from(event.body ? JSON.parse(event.body).iv : '', 'base64');
  const ciphertext = Buffer.from(event.body ? JSON.parse(event.body).ciphertext : '', 'base64');

  if (!encryptedAesKey || !iv || !ciphertext) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: "Missing encrypted data in the event" }),
    };
  }

  try {
    // Decode base64 values

    // Decrypt the AES key using KMS
    const decryptCommand = new DecryptCommand({
      CiphertextBlob: encryptedAesKey,
      KeyId: rsaKmsKeyId,
      EncryptionAlgorithm: "RSAES_OAEP_SHA_256",
    });

    const kmsResponse = await kmsClient.send(decryptCommand);
    const aesKey = kmsResponse.Plaintext;

    if (!aesKey) {
      return {
        statusCode: 500,
        body: JSON.stringify({ message: "Failed to decrypt AES key" }),
      };
    }

    // Decrypt the ciphertext using AES-CTR
    const decipher = crypto.createDecipheriv('aes-256-ctr', aesKey as Buffer, iv);
    const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]); // Return the plaintext data
    return {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      statusCode: 200,
      body: JSON.stringify({ plaintext: decrypted.toString('utf-8') }),
    };
  } catch (error) {
    console.error("Error decrypting data: ", error);
    return {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      statusCode: 500,
      body: JSON.stringify({ message: "Decryption failed" }),
    };
  }
};
