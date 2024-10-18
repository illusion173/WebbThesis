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

    # Read JSON input from stdin
    input_data = sys.stdin.read()

    # Parse the JSON input
    data = json.loads(input_data)

    # Extract the message from the event payload
    message = data.get('message')

    # Create a new data key for AES-256-GCM encryption
    response = kms_client.generate_data_key(
        KeyId=kms_key_id,
        KeySpec='AES_256'
    )
    
    plaintext_data_key = response['Plaintext']
    encrypted_data_key = response['CiphertextBlob']

    # Generate 16 secure random bytes
    iv = secrets.token_bytes(16)  # 16 bytes for AES-GCM IV

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
