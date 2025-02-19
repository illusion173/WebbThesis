import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms, RsaDecryptParameters } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

dotenv.config();
export async function rsa3072_decrypt_handler(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
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
    const keyName = process.env.RSA3072_KEY_NAME;

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

    // Extract the encrypted data
    const iv = base64.toByteArray(requestJson["iv"]);
    const ciphertext = base64.toByteArray(requestJson["ciphertext"]);
    const encryptedAesKey = base64.toByteArray(requestJson["encrypted_aes_key"]);

    const decryptParams: RsaDecryptParameters = { algorithm: KnownEncryptionAlgorithms.RSAOaep256, ciphertext: encryptedAesKey };

    // Decrypt the AES key using RSA-OAEP (SHA-256)
    const decryptResult = await cryptoClient.decrypt(decryptParams);
    const aesKey = decryptResult.result;

    // Decrypt the message using AES-CTR
    const decipher = crypto.createDecipheriv("aes-256-ctr", aesKey, iv);
    const decryptedMessage = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");

    let body_str = {
        message: decryptedMessage
    }

    return { jsonBody: body_str };
};

app.http('typescript_rsa3072_decrypt', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: rsa3072_decrypt_handler
});
