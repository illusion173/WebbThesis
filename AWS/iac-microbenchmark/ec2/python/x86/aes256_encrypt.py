#!/usr/bin/env python3
import boto3
import base64
import os
import secrets
import sys
import json
# Initialize encryption using AES-GCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def main():
    # Initialize KMS client
    kms_client = boto3.client('kms')

    # Get the KMS key ARN from environment variables
    kms_key_id = os.environ['AES_KMS_KEY_ARN']


    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)

    message = request_json["message"]


    # Create a new data key for AES-256-GCM encryption
    response = kms_client.generate_data_key(
        KeyId=kms_key_id,
        KeySpec='AES_256'
    )
    
    plaintext_data_key = response['Plaintext']
    encrypted_data_key = response['CiphertextBlob']

    # Generate 16 secure random bytes
    iv = secrets.token_bytes(12)  # 12 bytes for AES-GCM IV

    cipher = Cipher(algorithms.AES(plaintext_data_key), modes.GCM(iv))
    encryptor = cipher.encryptor()

    # Encrypt the message (no padding required in AES-GCM)
    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
    tag = encryptor.tag
    
    # Return the response without json.dumps
    encrypt_result =  {
        'encrypted_data_key': base64.b64encode(encrypted_data_key).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8'),
        'encrypted_message': base64.b64encode(ciphertext).decode('utf-8')
    }

    print(json.dumps(encrypt_result))

if __name__ == "__main__":
    main()
