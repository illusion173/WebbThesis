import * as AWS from 'aws-sdk';
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize the KMS client
const kmsClient = new AWS.KMS();

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {

    // Retrieve the original message and the base64 encoded signature from the event
    const message: string = Buffer.from(event.body ? JSON.parse(event.body).message : '', 'utf-8').toString();
    const signatureB64: string = Buffer.from(event.body ? JSON.parse(event.body).signature : '', 'utf-8').toString();

    const eccKmsKeyId: string = process.env.ECC256_KMS_KEY_ARN!;

    // Decode the signature from base64
    const signature: Buffer = Buffer.from(signatureB64, 'base64');

    try {
        // Verify the signature using KMS
        const response = await kmsClient.verify({
            KeyId: eccKmsKeyId,
            Message: Buffer.from(message, 'utf-8'),
            MessageType: 'RAW',
            Signature: signature,
            SigningAlgorithm: 'ECDSA_SHA_256' // Use 'ECDSA_SHA_384' for P-384
        }).promise();

        return {
            statusCode: 200,
            body: JSON.stringify({ verified: response.SignatureValid })
        };
    } catch (error) {
        console.error("Error verifying signature: ", error);
        return {
            statusCode: (error as any).statusCode || 500,
            body: JSON.stringify({ error: 'Verification failed' })
        };
    }
};
