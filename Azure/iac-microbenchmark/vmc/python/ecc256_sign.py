import json
import base64
import sys
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

def main():
    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]
    request_json = json.loads(request_json_raw)

    # Extract the message digest from the event payload
    message_digest = request_json.get('message_digest')
    message_digest_bytes = bytes.fromhex(message_digest)
    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["ECC256_KEY_NAME"]

    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url=key_vault_url, credential=credential)

    # Get the key from Azure Key Vault
    key = key_client.get_key(key_name)

    # Initialize the cryptography client for signing
    crypto_client = CryptographyClient(key, credential)

    # Sign the hash
    sign_result = crypto_client.sign(
        algorithm=SignatureAlgorithm.es256,  # Specify the signing algorithm
        digest=message_digest_bytes  # Pass the SHA-256 hash
    )

    # Encode the signature to base64 for easier transport
    signature_b64 = base64.b64encode(sign_result.signature).decode("utf-8")
    let base64url_digest = URL_SAFE_NO_PAD.encode(digest_bytes);
    print(json.dumps({"signature": signature_b64}))

if __name__ == "__main__":
    main()
