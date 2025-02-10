import base64
import json
import os
import sys
import secrets
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def main():
    # Get the input JSON from command-line arguments
        # Read input JSON from CLI argument
    input_json = json.loads(sys.argv[1])
    message = input_json.get("message")
    # Generate a random 256-bit AES key
    aes_key = secrets.token_bytes(32)
    
    # Generate a random IV (16 bytes for AES-CTR)
    iv = secrets.token_bytes(16)
    # Azure Key Vault configurations
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]  
    key_name = os.environ["RSA4096_KEY_NAME"]

    # Authenticate to Azure
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url=key_vault_url, credential=credential)
    crypto_client = CryptographyClient(key_client.get_key(key_name), credential)
    # Encrypt the message using AES-CTR
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()

    # Encrypt the AES key using RSA-OAEP (SHA-256)
    encrypt_result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep_256, aes_key)
    encrypted_aes_key = encrypt_result.ciphertext
    # Print the result as JSON
    print(json.dumps({
        'iv': base64.b64encode(iv).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8')
    }))

if __name__ == "__main__":
    main()
