import os
import base64
import json
import secrets
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="python_rsa3072_encrypt")
@app.route(route="rsa3072_encrypt")
def main(req: func.HttpRequest) -> func.HttpResponse:

    # Get environment variables
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]
    key_name = os.environ["RSA3072_KEY_NAME"]

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for rsa3072_encrypt is missing body.", status_code=400)

    try:
        # Authenticate using default azure creds in azure function
        credential = DefaultAzureCredential()
        key_client = KeyClient(vault_url=key_vault_url, credential=credential)

        # Get the key from Azure Key Vault
        key = key_client.get_key(key_name)

        # Initialize the cryptography client for operation
        crypto_client = CryptographyClient(key, credential)

        message = body.get("message")
        # Generate a random 256-bit AES key
        aes_key = secrets.token_bytes(32)
        
        # Generate a random IV (16 bytes for AES-CTR)
        iv = secrets.token_bytes(16)

        # Encrypt the message using AES-CTR
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()

        # Encrypt the AES key using RSA-OAEP (SHA-256)
        encrypt_result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep_256, aes_key)
        encrypted_aes_key = encrypt_result.ciphertext
        
        result_json_str = json.dumps({
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8')
        })

        return func.HttpResponse(f"{result_json_str}")
    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation rsa3072_encrypt {e} .", status_code=500)
