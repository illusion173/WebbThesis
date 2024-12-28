import base64
import json
import os
from botocore.exceptions import ClientError
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
# AWS KMS Client
kms_client = boto3.client('kms')

def lambda_handler(event, context):

    # Get the KMS key ID from environment variables or directly
    rsa_kms_key_id = os.environ['RSA2048_KMS_KEY_ARN']
    
    # Generate a random AES key
    aes_key = secrets.token_bytes(32)

    iv = secrets.token_bytes(16)

    # Encrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Assuming the data to encrypt is passed in the event
    plaintext = event.get('message').encode('utf-8')
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Encrypt the AES key using KMS
    try:
        response = kms_client.encrypt(
            KeyId=rsa_kms_key_id,
            Plaintext=aes_key,
            EncryptionAlgorithm="RSAES_OAEP_SHA_256"
        )
        encrypted_aes_key = response['CiphertextBlob']
    except ClientError as e:
        print(f"Error encrypting AES key: {e}")
        return {
            'statusCode': 500,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps('Encryption failed')
        }

    return {
        'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
        'body' : json.dumps({
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8')
        })
        
    }
