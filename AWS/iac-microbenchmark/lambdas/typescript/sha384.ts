import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';
import { KMSClient, GenerateMacCommand } from '@aws-sdk/client-kms';
import * as process from 'process';

// Initialize the AWS KMS client
const kmsClient = new KMSClient({
  region: 'us-east-1' // Specify the desired region
});// Define the signing algorithm

const SIGN_ALGORITHM = 'HMAC_SHA_384';

export const handler = async (event: any, context: Context): Promise<any> => {

  // Extract the message from the event body, assuming it's passed as a JSON string
  const body = event.body ? JSON.parse(event.body) : {};
  const message: string = body.message || '';

  // Retrieve the KMS key ARN from environment variables
  const shaKmsKeyId: string = process.env.SHA384_KMS_KEY_ARN!;

  // Convert the message to a byte buffer
  const messageBytes = Buffer.from(message, 'utf-8');


  // Check if the KMS key ARN is provided
  if (!shaKmsKeyId) {
    throw new Error("SHA384_KMS_KEY_ARN environment variable is not set");

  }

  try {

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


    return {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      statusCode: 200,
      body: JSON.stringify({
        signature: signature
      }),
    };

  } catch (error) {
    console.error('Error signing message:', error);
    return {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "content-type": "application/json"
      },
      statusCode: 500,
      body: JSON.stringify({
        error: 'An error occurred while signing the message'
      }),
    };
  }
};
