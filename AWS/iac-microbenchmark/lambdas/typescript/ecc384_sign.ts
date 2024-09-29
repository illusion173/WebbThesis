import * as AWS from 'aws-sdk';
import { Context, APIGatewayProxyResult, APIGatewayEvent } from 'aws-lambda';

// Initialize the KMS client
const kmsClient = new AWS.KMS();

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {

    const message: string = Buffer.from(event.body ? JSON.parse(event.body).message : '', 'utf-8').toString();

    //const message: string = event.message; // The message to sign
    const eccKmsKeyId: string = process.env.ECC384_KMS_KEY_ARN!;

    try {
        // Sign the message using KMS
        const response = await kmsClient.sign({
            KeyId: eccKmsKeyId,
            Message: Buffer.from(message, 'utf-8'),
            MessageType: 'RAW',
            SigningAlgorithm: 'ECDSA_SHA_256' // Use 'ECDSA_SHA_384' for P-384
        }).promise();

        const signature = response.Signature as Uint8Array;

        // Encode the signature to base64 for easier transport
        const signatureB64 = Buffer.from(signature).toString('base64');

        return {
            statusCode: 200,
            body: JSON.stringify({ signature: signatureB64 })
        };

    } catch (error) {
        console.error("Error decrypting data: ", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: "Decryption failed" }),
        };
    }
};
