import base64
import json
import os
import sys
from azure.identity import AzureCliCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def main():
    # Read encrypted input JSON from CLI argument
    encrypted_json = json.loads(sys.argv[1])

    # Extract base64-encoded values and decode them
    iv = base64.b64decode(encrypted_json['iv'])
    ciphertext = base64.b64decode(encrypted_json['ciphertext'])
    encrypted_aes_key = base64.b64decode(encrypted_json['encrypted_aes_key'])

    # Azure Key Vault configurations
    key_vault_url = os.environ["AZURE_KEY_VAULT_URL"]  
    key_name = os.environ["RSA4096_KEY_NAME"]

    # Authenticate to Azure
    credential = AzureCliCredential()
    key_client = KeyClient(vault_url=key_vault_url, credential=credential)
    crypto_client = CryptographyClient(key_client.get_key(key_name), credential)

    # Decrypt the AES key using Azure Key Vault RSA key
    decrypt_result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep_256, encrypted_aes_key)
    aes_key = decrypt_result.plaintext

    # Decrypt the ciphertext using AES-CTR
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Print the decrypted message
    print(json.dumps({"decrypted_message": plaintext.decode('utf-8')}))

if __name__ == "__main__":
    main()
