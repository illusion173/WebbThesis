import boto3
import base64
import json
import os

# Initialize encryption using AES-GCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cryptography.hazmat.primitives import padding

def lambda_handler(event, context):

    # Initialize KMS client
    kms_client = boto3.client('kms')

    # Get the KMS key ARN from environment variables
    kms_key_id = os.environ['AES_KMS_KEY_ARN']
    
    # Extract the message from the API Gateway event
    message = event.get('message')
    
    # Create a new data key for AES-256-GCM encryption
    response = kms_client.generate_data_key(
        KeyId=kms_key_id,
        KeySpec='AES_256'
    )
    
    plaintext_data_key = response['Plaintext']
    encrypted_data_key = response['CiphertextBlob']
    
    iv = os.urandom(16)  # 16 bytes for AES-GCM IV
    cipher = Cipher(algorithms.AES(plaintext_data_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    
    # Pad the message to be encrypted
    padder = padding.PKCS7(16).padder()
    padded_message = padder.update(message.encode('utf-8')) + padder.finalize()
    
    # Encrypt the message
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()
    tag = encryptor.tag
    
    # Encode results as base64
    encrypted_message = base64.b64encode(iv + tag + ciphertext).decode('utf-8')
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'encrypted_data_key': base64.b64encode(encrypted_data_key).decode('utf-8'),
            'encrypted_message': encrypted_message
        })
    }
