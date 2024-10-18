#!/usr/bin/env python3
import base64
import json
import os
import sys
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# AWS KMS Client
kms_client = boto3.client('kms')

def main():
    # Read JSON input from stdin
    input_data = sys.stdin.read()
    # Parse the JSON input
    data = json.loads(input_data)

    # Get the KMS key ID from environment variables
    rsa_kms_key_id = os.environ['RSA2048_KMS_KEY_ID']
    
    # Get the data from the input payload
    encrypted_aes_key_b64 = data.get('encrypted_aes_key')
    iv_b64 = data.get('iv')
    ciphertext_b64 = data.get('ciphertext')

    # Decode base64 values
    encrypted_aes_key = base64.b64decode(encrypted_aes_key_b64)
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    # Decrypt the AES key using KMS
    response = kms_client.decrypt(
        CiphertextBlob=encrypted_aes_key,
        KeyId=rsa_kms_key_id,
        EncryptionAlgorithm="RSAES_OAEP_SHA_256"
    )
    aes_key = response['Plaintext']

    # Decrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Return the plaintext as a JSON response
    result = {
        'plaintext': plaintext.decode('utf-8')
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
