import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms, RsaDecryptParameters } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

dotenv.config();

async function main() {
  try {
    // Get the input argument (assuming it's a JSON string)
    const requestJsonRaw = process.argv[2];
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the encrypted data
    const iv = base64.toByteArray(requestJson.iv);
    const ciphertext = base64.toByteArray(requestJson.ciphertext);
    const encryptedAesKey = base64.toByteArray(requestJson.encrypted_aes_key);

    // Get environment variables
    const keyVaultUrl = process.env.AZURE_KEY_VAULT_URL;
    const keyName = process.env.RSA3072_KEY_NAME;

    if (!keyVaultUrl || !keyName) {
      throw new Error("Missing required environment variables.");
    }

    // Authenticate using DefaultAzureCredential
    const credential = new DefaultAzureCredential();
    const keyClient = new KeyClient(keyVaultUrl, credential);

    // Get the key from Azure Key Vault
    const key = await keyClient.getKey(keyName);

    if (!key.id) {
      throw new Error("Key ID is undefined.");
    }

    // Initialize the cryptography client for decryption
    const cryptoClient = new CryptographyClient(key.id, credential);

    const decryptParams: RsaDecryptParameters = { algorithm: KnownEncryptionAlgorithms.RSAOaep256, ciphertext: encryptedAesKey };

    // Decrypt the AES key using RSA-OAEP (SHA-256)
    const decryptResult = await cryptoClient.decrypt(decryptParams);
    const aesKey = decryptResult.result;

    // Decrypt the message using AES-CTR
    const decipher = crypto.createDecipheriv("aes-256-ctr", aesKey, iv);
    const decryptedMessage = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");

    // Print the decrypted message
    console.log(JSON.stringify({ message: decryptedMessage }));
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main();
