import * as AWS from 'aws-sdk';
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize the AWS KMS client
const kmsClient = new AWS.KMS();

const SIGN_ALGORITHM = 'HMAC_SHA_256';

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {
    
    // Extract the message from the event body, assuming it's passed as a JSON string
    const body = event.body ? JSON.parse(event.body) : {};
    const message: string = body.message || '';

    // Retrieve the KMS key ARN from environment variables
    const shaKmsKeyId: string = process.env.SHA256_KMS_KEY_ARN!;

    // Convert the message to a byte buffer
    const messageBytes = Buffer.from(message, 'utf-8');

    try {
        // Use KMS to sign (HMAC) the message
        const response = await kmsClient.sign({
            KeyId: shaKmsKeyId,
            Message: messageBytes,
            MessageType: 'RAW',
            SigningAlgorithm: SIGN_ALGORITHM
        }).promise();

        // Base64 encode the signature for output using Buffer
        const signature = Buffer.from(response.Signature as Uint8Array).toString('base64');

        return {
            statusCode: 200,
            body: JSON.stringify({
                signature: signature
            }),
        };

    } catch (error) {
        console.error('Error signing message:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'An error occurred while signing the message'
            }),
        };
    }
};
