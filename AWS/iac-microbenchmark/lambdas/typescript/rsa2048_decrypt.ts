import { KMSClient, DecryptCommand } from "@aws-sdk/client-kms";
import * as crypto from "crypto";
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize KMS Client
const kmsClient = new KMSClient({});

export const handler = async (event: any, context: Context): Promise<any> => {

  // Get the KMS key ID from environment variables 
  const rsaKmsKeyId = process.env.RSA2048_KMS_KEY_ARN;

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

  // Get encrypted data from the event body
  const body = event.body ? JSON.parse(event.body) : {};
  const encryptedAesKeyB64 = body.encrypted_aes_key;
  const ivB64 = body.iv;
  const ciphertextB64 = body.ciphertext;

  if (!encryptedAesKeyB64 || !ivB64 || !ciphertextB64) {
    return {
      statusCode: 400,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ message: "Missing encrypted data in the event" }),
    };
  }

  try {
    // Decode base64 values
    const encryptedAesKey = Buffer.from(encryptedAesKeyB64, 'base64');
    const iv = Buffer.from(ivB64, 'base64');
    const ciphertext = Buffer.from(ciphertextB64, 'base64');

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
        headers: {
          "Access-Control-Allow-Origin": "*",
          "content-type": "application/json"
        },
        body: JSON.stringify({ message: "Failed to decrypt AES key" }),
      };
    }

    // Decrypt the ciphertext using AES-CTR
    const decipher = crypto.createDecipheriv('aes-256-ctr', aesKey as Buffer, iv);
    const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);

    // Return the plaintext data
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        plaintext: decrypted.toString('utf-8'),
      }),
    };
  } catch (error) {
    console.error("Error decrypting data: ", error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ message: "Decryption failed" }),
    };
  }
};
