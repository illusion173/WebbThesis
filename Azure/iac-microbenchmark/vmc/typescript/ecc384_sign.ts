import { AzureCliCredential } from "@azure/identity";
import { KeyClient, KeyVaultKey, CryptographyClient, KnownSignatureAlgorithms } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";

dotenv.config();

async function main() {
  try {
    // Get the input argument (assuming it's a JSON string)
    const requestJsonRaw = process.argv[2];
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message digest from the event payload
    const messageDigestHex: string = requestJson.message_digest;
    const messageDigestBytes = Buffer.from(messageDigestHex, "hex");

    // Get environment variables
    const keyVaultUrl = process.env.AZURE_KEY_VAULT_URL;
    const keyName = process.env.ECC384_KEY_NAME;

    if (!keyVaultUrl || !keyName) {
      throw new Error("Missing required environment variables.");
    }

    // Authenticate using AzureCliCredential
    const credential = new AzureCliCredential();
    const keyClient = new KeyClient(keyVaultUrl, credential);

    // Get the key from Azure Key Vault
    const key: KeyVaultKey = await keyClient.getKey(keyName);

    if (!key.id) {
      throw new Error("Key ID is undefined.");
    }

    // Initialize the cryptography client for signing
    const cryptoClient = new CryptographyClient(key.id, credential);

    // Sign the hash
    const signResult = await cryptoClient.sign(KnownSignatureAlgorithms.ES384, messageDigestBytes);

    // Encode the signature to base64
    const signatureB64 = base64.fromByteArray(signResult.result);

    console.log(JSON.stringify({ signature: signatureB64 }));
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main();
