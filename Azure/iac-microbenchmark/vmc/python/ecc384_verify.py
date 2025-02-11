import json
import base64
import sys
import os
from azure.identity import AzureCliCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

def main():
    # Get the input JSON from command-line arguments
    request_json_raw = sys.argv[1]
    request_json = json.loads(request_json_raw)

    # Extract message and signature from the input
    message_digest = request_json.get("message_digest")

    message_digest_bytes = bytes.fromhex(message_digest)

    signature_b64 = request_json.get("signature")

    is_valid = False

    try:
        # Get environment variables
        key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
        key_name = os.environ["ECC384_KEY_NAME"]

        # Authenticate using AzureCliCredential
        credential = AzureCliCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Retrieve the ECC P-384 key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client
        crypto_client = CryptographyClient(key, credential)

        # Decode the Base64-encoded signature
        signature = base64.b64decode(signature_b64)

        # Verify the signature using ECC P-384 (ES384)
        verify_result = crypto_client.verify(
            algorithm=SignatureAlgorithm.es384,
            digest=message_digest_bytes,
            signature=signature
        )

        is_valid = verify_result.is_valid

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return False

    # Print the result as JSON
    print(json.dumps({"is_valid": is_valid}))

if __name__ == "__main__":
    main()
