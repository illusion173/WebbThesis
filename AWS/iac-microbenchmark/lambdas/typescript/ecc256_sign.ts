import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';
import { KMSClient, SignCommand } from '@aws-sdk/client-kms';
import * as process from 'process';
import * as base64 from 'base64-js';

// Initialize the AWS KMS client with the specified region
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});


export const handler = async (event: any, context: Context): Promise<any> => {

  const message: string = Buffer.from(event.body ? JSON.parse(event.body).message : '', 'utf-8').toString();

  const eccKmsKeyId: string = process.env.ECC256_KMS_KEY_ARN!;

  try {


    // Sign the message using KMS
    const signCommand = new SignCommand({
      KeyId: eccKmsKeyId,
      Message: Buffer.from(message, 'utf-8'),
      MessageType: 'RAW',
      SigningAlgorithm: 'ECDSA_SHA_256' // Use 'ECDSA_SHA_384' for P-384
    });

    const response = await kmsClient.send(signCommand);
    const signature = response.Signature as Uint8Array;

    // Encode the signature to base64 for easier transport
    const signatureB64 = base64.fromByteArray(signature);

    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ signature: signatureB64 })
    };

  } catch (error) {
    console.error("Error signing data: ", error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      body: JSON.stringify({ message: "Signing failed" }),
    };
  }
};
