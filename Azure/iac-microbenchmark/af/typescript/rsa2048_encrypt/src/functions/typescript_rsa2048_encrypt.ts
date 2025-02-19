import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms, RsaEncryptParameters } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

dotenv.config();
export async function rsa2048_encrypt_handler(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
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
    const keyName = process.env.RSA2048_KEY_NAME;

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

    // Extract the message from the event payload
    const message: string = requestJson['message'];

    // Generate a random 256-bit AES key
    const aesKey = crypto.randomBytes(32);

    // Generate a random IV (16 bytes for AES-CTR)
    const iv = crypto.randomBytes(16);



    // Encrypt the message using AES-CTR
    const cipher = crypto.createCipheriv("aes-256-ctr", aesKey, iv);
    const ciphertext = Buffer.concat([cipher.update(message, "utf8"), cipher.final()]);

    const encryptParams: RsaEncryptParameters = { algorithm: KnownEncryptionAlgorithms.RSAOaep256, plaintext: aesKey }

    // Encrypt the AES key using RSA-OAEP (SHA-256)
    const encryptResult = await cryptoClient.encrypt(
        encryptParams
    );

    const encryptedAesKey = encryptResult.result;

    let body_str = {
        iv: base64.fromByteArray(iv),
        ciphertext: base64.fromByteArray(ciphertext),
        encrypted_aes_key: base64.fromByteArray(encryptedAesKey)
    }

    return { jsonBody: body_str };
};

app.http('typescript_rsa2048_encrypt', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: rsa2048_encrypt_handler
});
