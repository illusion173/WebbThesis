import os
import base64
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="python_ecc256_sign")
@app.route(route="ecc256_sign")
def main(req: func.HttpRequest) -> func.HttpResponse:

    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["ECC256_KEY_NAME"]

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for ecc256_sign is missing body.", status_code=400)

    # main code here
    try:

        # Authenticate using default azure creds in azure function
        credential = DefaultAzureCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Get the key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client for operation
        crypto_client = CryptographyClient(key, credential)
        message_digest = body.get("message_digest")

        message_digest_bytes = bytes.fromhex(message_digest)
        # Sign the hash
        sign_result = crypto_client.sign(
            algorithm=SignatureAlgorithm.es256,  # Specify the signing algorithm
            digest=message_digest_bytes  # Pass the SHA-256 hash
        )

        # Encode the signature to base64 for easier transport
        signature_b64 = base64.b64encode(sign_result.signature).decode("utf-8")

        result_json_str = json.dumps({"signature": signature_b64})

        return func.HttpResponse(f"{result_json_str}")
    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation ecc256_sign {e} .", status_code=500)
