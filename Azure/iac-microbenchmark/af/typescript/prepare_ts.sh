#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do

    echo "Setting up project: $PROJECT"
    mkdir -p $PROJECT
    # go into new project
    cd "$PROJECT" || exit
    func init --typescript
    rm package.json

    cat <<EOF >package.json
{
  "name": "",
  "version": "1.0.0",
  "description": "",
  "main": "dist/src/functions/*.js",
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "clean": "rimraf dist",
    "prestart": "npm run clean && npm run build",
    "start": "func start",
    "test": "echo \"No tests yet...\""
  },
  "dependencies": {
    "@azure/functions": "^4.0.0",
    "@azure/identity": "^4.6.0",
    "@azure/keyvault-keys": "^4.9.0",
    "base64-js": "^1.5.1",
    "dotenv": "^16.4.7"
  },
  "devDependencies": {
    "azure-functions-core-tools": "^4.x",
    "@types/node": "^22.13.1",
    "typescript": "5.6.3",
    "rimraf": "^5.0.0"
  }
}
EOF
    npm install

    cd src/functions

    cat <<EOF >typescript_${PROJECT}.ts
import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { DefaultAzureCredential } from "@azure/identity";
import { KeyClient, CryptographyClient, KnownEncryptionAlgorithms,KnownSignatureAlgorithms, RsaEncryptParameters, RsaDecryptParameters} from "@azure/keyvault-keys";
import * as base64 from "base64-js";
import * as dotenv from "dotenv";
import * as crypto from "crypto";

dotenv.config();
export async function ${PROJECT}_handler(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
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

    let body_str = {
        "": "",
    }

    return { jsonBody: body_str };
};

app.http('typescript_${PROJECT}', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: ${PROJECT}_handler
});
EOF


    # Leave src/functions
    cd ../..
    echo "Done setting up ${PROJECT}"

    # return parent
    cd ..

done

echo "Done preparing typescript Azure Functions."
