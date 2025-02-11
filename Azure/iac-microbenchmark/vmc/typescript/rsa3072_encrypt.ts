import { AzureCliCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms, RsaEncryptParameters } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

dotenv.config();

async function main() {
    try {
        // Get the input argument (assuming it's a JSON string)
        const requestJsonRaw = process.argv[2];
        const requestJson = JSON.parse(requestJsonRaw);

        // Extract the message from the event payload
        const message: string = requestJson.message;

        // Generate a random 256-bit AES key
        const aesKey = crypto.randomBytes(32);

        // Generate a random IV (16 bytes for AES-CTR)
        const iv = crypto.randomBytes(16);

        // Get environment variables
        const keyVaultUrl = process.env.AZURE_KEY_VAULT_URL;
        const keyName = process.env.RSA3072_KEY_NAME;

        if (!keyVaultUrl || !keyName) {
            throw new Error("Missing required environment variables.");
        }

        // Authenticate using AzureCliCredential
        const credential = new AzureCliCredential();
        const keyClient = new KeyClient(keyVaultUrl, credential);

        // Get the key from Azure Key Vault
        const key = await keyClient.getKey(keyName);

        if (!key.id) {
            throw new Error("Key ID is undefined.");
        }

        // Initialize the cryptography client for encryption
        const cryptoClient = new CryptographyClient(key.id, credential);

        // Encrypt the message using AES-CTR
        const cipher = crypto.createCipheriv("aes-256-ctr", aesKey, iv);
        const ciphertext = Buffer.concat([cipher.update(message, "utf8"), cipher.final()]);

        const encryptParams: RsaEncryptParameters = { algorithm: KnownEncryptionAlgorithms.RSAOaep256, plaintext: aesKey }

        // Encrypt the AES key using RSA-OAEP (SHA-256)
        const encryptResult = await cryptoClient.encrypt(
            encryptParams
        );

        const encryptedAesKey = encryptResult.result;

        // Print the result as JSON
        console.log(JSON.stringify({
            iv: base64.fromByteArray(iv),
            ciphertext: base64.fromByteArray(ciphertext),
            encrypted_aes_key: base64.fromByteArray(encryptedAesKey)
        }));
    } catch (error) {
        console.error("Error:", error);
        process.exit(1);
    }
}

main();
