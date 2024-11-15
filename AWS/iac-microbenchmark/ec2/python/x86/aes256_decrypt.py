#!/usr/bin/env python3
import boto3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys

def main():
    # Initialize KMS client
    kms_client = boto3.client('kms')

     # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)

    # Extract the encrypted data key and encrypted message from the data
    encrypted_data_key = base64.b64decode(request_json.get('encrypted_data_key'))
    ciphertext = base64.b64decode(request_json.get('encrypted_message'))
    iv = base64.b64decode(request_json.get('iv'))
    tag = base64.b64decode(request_json.get('tag'))
    
    # Decrypt the data key using KMS
    response = kms_client.decrypt(
        CiphertextBlob=encrypted_data_key
    )

    plaintext_data_key = response['Plaintext']
    
    # Initialize decryption using AES-GCM
    cipher = Cipher(algorithms.AES(plaintext_data_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    
    # Decrypt the message
    plaintext_message_bytes = decryptor.update(ciphertext) + decryptor.finalize()

    plaintext_message = plaintext_message_bytes.decode("utf-8")

    

    decrypt_message = {"message" : plaintext_message}

    print(json.dumps(decrypt_message))

if __name__ == "__main__":
    main()
