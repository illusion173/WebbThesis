import json
import base64
import sys
import os
import hashlib
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

def main():
    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]
    request_json = json.loads(request_json_raw)

    # Extract the message from the event payload
    message = request_json.get('message')

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

    # Compute the SHA-256 hash of the message
    message_digest = hashlib.sha256(message.encode("utf-8")).digest()

    # Sign the hash
    sign_result = crypto_client.sign(
        algorithm=SignatureAlgorithm.es256,  # Specify the signing algorithm
        digest=message_digest  # Pass the SHA-256 hash
    )

    # Encode the signature to base64 for easier transport
    signature_b64 = base64.b64encode(sign_result.signature).decode("utf-8")

    print(json.dumps({"signature": signature_b64}))

if __name__ == "__main__":
    main()
