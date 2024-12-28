import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';
import { KMSClient, VerifyCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as base64 from 'base64-js';

// Initialize the AWS KMS client with the specified region
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {
  // Retrieve the original message and the base64 encoded signature from the event
  const body = event.body ? JSON.parse(event.body) : {};
  const message: string = body.message || '';
  const signatureB64: string = body.signature || ''; // Extract signature from body

  const eccKmsKeyId: string = process.env.ECC256_KMS_KEY_ARN!;

  if (!eccKmsKeyId) {
    throw new Error("ECC256_KMS_KEY_ARN environment variable is not set");
  }

  // Decode the base64-encoded signature
  const signature = base64.toByteArray(signatureB64);

  try {

    // Verify the signature using KMS
    const verifyCommand = new VerifyCommand({
      KeyId: eccKmsKeyId,
      Message: Buffer.from(message, 'utf-8'),
      MessageType: 'RAW',
      Signature: signature,
      SigningAlgorithm: 'ECDSA_SHA_256' // Use 'ECDSA_SHA_384' for P-384
    });

    const response = await kmsClient.send(verifyCommand);
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ verified: response.SignatureValid })
    };
  } catch (error) {
    console.error("Error verifying signature: ", error);
    return {
      statusCode: (error as any).statusCode || 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ error: 'Verification failed' })
    };
  }
};
