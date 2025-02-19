import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms, RsaEncryptParameters } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

export async function HttpExample(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
    context.log(`Http function processed request for url "${request.url}"`);

    let requestJson: unknown; // to be json

    if (request.body) {

        requestJson = await request.json(); // Parses JSON body

    } else {
        return {
            status: 400,
            body: "Invalid JSON in request body"
        };
    }

    // Extract the message from the event payload
    const message: string = requestJson["message"]

    // Generate a random 256-bit AES key
    const aesKey = crypto.randomBytes(32);

    // Generate a random IV (16 bytes for AES-CTR)
    const iv = crypto.randomBytes(16);


    return { body: `Hello, ${name}!` };
};

app.http('HttpExample', {
    methods: ['GET', 'POST'],
    authLevel: 'anonymous',
    handler: HttpExample
});
