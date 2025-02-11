import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownSignatureAlgorithms } from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";

dotenv.config();

async function main() {
  try {
    // Get the input argument (assuming it's a JSON string)
    const requestJsonRaw = process.argv[2];
    const requestJson = JSON.parse(requestJsonRaw);

    // Extract the message digest and signature from the event payload
    const messageDigestHex: string = requestJson.message_digest;
    const signatureB64: string = requestJson.signature;

    // Convert message digest and signature to byte arrays
    const messageDigestBytes = Buffer.from(messageDigestHex, "hex");
    const signatureBytes = base64.toByteArray(signatureB64);

    // Get environment variables
    const keyVaultUrl = process.env.AZURE_KEY_VAULT_URL;
    const keyName = process.env.ECC384_KEY_NAME;

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

    // Initialize the cryptography client for verification
    const cryptoClient = new CryptographyClient(key.id, credential);

    // Verify the signature
    const verifyResult = await cryptoClient.verify(
      KnownSignatureAlgorithms.ES384,
      messageDigestBytes,
      signatureBytes
    );

    const is_valid = verifyResult.result

    console.log(JSON.stringify({ is_valid: is_valid }));
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main();
