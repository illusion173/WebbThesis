import base64
import json
import os
from botocore.exceptions import ClientError
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# AWS KMS Client
kms_client = boto3.client('kms')

def lambda_handler(event, context):
    # Get the KMS key ID from environment variables or directly
    rsa_kms_key_id = os.environ['RSA2048_KMS_KEY_ID']
    
    # Get the data from the event
    encrypted_aes_key_b64 = event.get('encrypted_aes_key')
    iv_b64 = event.get('iv')
    ciphertext_b64 = event.get('ciphertext')

    # Decode base64 values
    encrypted_aes_key = base64.b64decode(encrypted_aes_key_b64)
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    # Decrypt the AES key using KMS
    try:
        response = kms_client.decrypt(
            CiphertextBlob=encrypted_aes_key,
            KeyId=rsa_kms_key_id,
            EncryptionAlgorithm="RSAES_OAEP_SHA_256"
        )
        aes_key = response['Plaintext']
    except ClientError as e:
        print(f"Error decrypting AES key: {e}")
        return {
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'statusCode': 500,
            'body': json.dumps('Decryption failed')
        }

    # Decrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return {
        'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
        'body': plaintext.decode('utf-8')
    }
