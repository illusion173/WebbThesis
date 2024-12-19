import { KMSClient, GenerateDataKeyCommand } from "@aws-sdk/client-kms";
import { randomBytes, createCipheriv } from "crypto";
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// handler for AWS Lambda
export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {
  console.log(`Event: ${JSON.stringify(event, null, 2)}`);
  console.log(`Context: ${JSON.stringify(context, null, 2)}`);

  // Initialize the KMS client
  const kmsClient = new KMSClient({ region: 'us-east-1' });

  // Get the KMS Key ARN from environment variables
  const kmsKeyId = process.env.AES_KMS_KEY_ARN as string;

  // Extract the message from the event body, assuming it's passed as a JSON string
  const body = event.body ? JSON.parse(event.body) : {};
  const message = body.message;

  if (!message) {
    return {
      statusCode: 400,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ error: "Message is required" }),
    };
  }

  // Create a new data key for AES-256 encryption using KMS
  const dataKeyCommand = new GenerateDataKeyCommand({
    KeyId: kmsKeyId,
    KeySpec: "AES_256",
  });

  try {
    const dataKeyResponse = await kmsClient.send(dataKeyCommand);

    const plaintextDataKey = dataKeyResponse.Plaintext as Uint8Array;
    const encryptedDataKey = dataKeyResponse.CiphertextBlob as Uint8Array;

    // Convert encryptedDataKey to a Buffer before encoding to base64
    const encryptedDataKeyBuffer = Buffer.from(encryptedDataKey);

    // Generate a 12-byte IV for AES-GCM
    const iv = randomBytes(12); // 12 bytes IV for GCM mode

    // Encrypt the message using AES-GCM
    const cipher = createCipheriv("aes-256-gcm", plaintextDataKey, iv);

    const ciphertext = Buffer.concat([
      cipher.update(Buffer.from(message, "utf-8")),
      cipher.final(),
    ]);

    const tag = cipher.getAuthTag();

    // Return the encrypted message and relevant details in Base64 encoding
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        encrypted_data_key: encryptedDataKeyBuffer.toString("base64"), // Convert to base64
        iv: iv.toString("base64"),
        tag: tag.toString("base64"),
        encrypted_message: ciphertext.toString("base64"),
      }),
    };

  } catch (error) {
    console.error('Error generating data key or encrypting message:', error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ error: 'An error occurred during the encryption process' }),
    };
  }
};
