#!/usr/bin/env python3
import boto3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys

def main():
    # Read JSON input from stdin
    input_data = sys.stdin.read()

# Parse the JSON input
    data = json.loads(input_data)

    # Initialize KMS client
    kms_client = boto3.client('kms')
    
    # Extract the encrypted data key and encrypted message from the data
    encrypted_data_key = base64.b64decode(data.get('encrypted_data_key'))
    ciphertext = base64.b64decode(data.get('encrypted_message'))
    iv = base64.b64decode(data.get('iv'))
    tag = base64.b64decode(data.get('tag'))
    
    # Decrypt the data key using KMS
    response = kms_client.decrypt(
        CiphertextBlob=encrypted_data_key
    )

    plaintext_data_key = response['Plaintext']
    
    # Initialize decryption using AES-GCM
    cipher = Cipher(algorithms.AES(plaintext_data_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    
    # Decrypt the message
    plaintext_message = decryptor.update(ciphertext) + decryptor.finalize()
    

    decrypt_message = {"Message" : plaintext_message}

    print(json.dumps(decrypt_message))

if __name__ == "__main__":
    main()
