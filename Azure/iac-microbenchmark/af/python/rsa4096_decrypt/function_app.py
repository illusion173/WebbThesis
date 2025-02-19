import os
import base64
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="python_rsa4096_decrypt")
@app.route(route="rsa4096_decrypt")
def main(req: func.HttpRequest) -> func.HttpResponse:

    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["RSA4096_KEY_NAME"]

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for rsa4096_decrypt is missing body.", status_code=400)

    # main code here
    try:
        # Authenticate using default azure creds in azure function
        credential = DefaultAzureCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Get the key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client for operation
        crypto_client = CryptographyClient(key, credential)
        # Extract base64-encoded values and decode them
        iv = base64.b64decode(body['iv'])
        ciphertext = base64.b64decode(body['ciphertext'])
        encrypted_aes_key = base64.b64decode(body['encrypted_aes_key'])

        # Decrypt the AES key using Azure Key Vault RSA key
        decrypt_result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep_256, encrypted_aes_key)
        aes_key = decrypt_result.plaintext

        # Decrypt the ciphertext using AES-CTR
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        result_json_str = json.dumps({"decrypted_message": plaintext.decode('utf-8')})

        return func.HttpResponse(f"{result_json_str}")
    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation rsa4096_decrypt {e} .", status_code=500)
