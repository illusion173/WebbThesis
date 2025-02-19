import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownSignatureAlgorithms } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";

dotenv.config();
export async function ecc256_sign_handler(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
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
    let messageDigestHex: String = requestJson["message_digest"]

    const messageDigestBytes = Buffer.from(messageDigestHex, "hex");

    // Sign the hash
    const signResult = await cryptoClient.sign(KnownSignatureAlgorithms.ES256, messageDigestBytes);

    // Encode the signature to base64
    const signatureB64 = base64.fromByteArray(signResult.result);

    let body_str = {
        signature: signatureB64,
    }

    return { jsonBody: body_str };
};

app.http('typescript_ecc256_sign', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: ecc256_sign_handler
});
