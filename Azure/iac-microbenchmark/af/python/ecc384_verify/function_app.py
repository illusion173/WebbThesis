import os
import base64
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient,SignatureAlgorithm

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="python_ecc384_verify")
@app.route(route="ecc384_verify")
def main(req: func.HttpRequest) -> func.HttpResponse:

    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["ECC384_KEY_NAME"]

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for ecc384_verify is missing body.", status_code=400)

    # main code here
    try:
        # Authenticate using default azure creds in azure function
        credential = DefaultAzureCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Get the key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client for operation
        crypto_client = CryptographyClient(key, credential)

        # Extract message and signature from the input
        message_digest = body.get("message_digest")
        message_digest_bytes = bytes.fromhex(message_digest)
        signature_b64 = body.get("signature")

        signature = base64.b64decode(signature_b64)

        # Verify the signature using ECC P-384 (ES256)
        verify_result = crypto_client.verify(
            algorithm=SignatureAlgorithm.es384,
            digest=message_digest_bytes,
            signature=signature
        )

        is_valid = verify_result.is_valid

        result_json_str = json.dumps({"is_valid": is_valid})

        return func.HttpResponse(f"{result_json_str}")
    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation ecc384_verify {e} .", status_code=500)
