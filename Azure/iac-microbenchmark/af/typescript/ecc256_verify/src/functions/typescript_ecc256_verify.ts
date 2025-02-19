import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownSignatureAlgorithms } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";

dotenv.config();
export async function ecc256_verify_handler(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
    let requestJson: unknown; // to be json

    if (request.body) {

        requestJson = await request.json(); // Parses JSON body

    } else {
        return {
            status: 400,
            body: "Invalid JSON in request body"
        };
    }

    // Get environment variables
    const keyVaultUrl = process.env.AZURE_KEY_VAULT_URL;
    const keyName = process.env.ECC256_KEY_NAME;

    if (!keyVaultUrl || !keyName) {
        return {
            status: 500,
            body: "Missing required environment variables."
        };
    }

    const credential = new DefaultAzureCredential();
    const keyClient = new KeyClient(keyVaultUrl, credential);

    // Get the key from Azure Key Vault
    const key = await keyClient.getKey(keyName);

    if (!key.id) {
        return {
            status: 500,
            body: "Key ID is undefined."
        };
    }

    // Initialize the cryptography client for encryption
    const cryptoClient = new CryptographyClient(key.id, credential);

    // Extract the message digest and signature from the event payload
    const messageDigestHex: string = requestJson["message_digest"];

    const signatureB64: string = requestJson["signature"];

    // Convert message digest and signature to byte arrays
    const messageDigestBytes = Buffer.from(messageDigestHex, "hex");
    const signatureBytes = base64.toByteArray(signatureB64);

    // Verify the signature
    const verifyResult = await cryptoClient.verify(
        KnownSignatureAlgorithms.ES256,
        messageDigestBytes,
        signatureBytes
    );

    const is_valid = verifyResult.result

    let body_str = {
        is_valid: is_valid,
    }

    return { jsonBody: body_str };
};

app.http('typescript_ecc256_verify', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: ecc256_verify_handler
});
