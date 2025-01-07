import boto3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def lambda_handler(event, context):
    # Initialize KMS client
    kms_client = boto3.client('kms')
    
    # Extract the encrypted data key and encrypted message from the event
    encrypted_data_key = base64.b64decode(event.get('encrypted_data_key'))
    ciphertext = base64.b64decode(event.get('encrypted_message'))
    iv = base64.b64decode(event.get('iv'))
    tag = base64.b64decode(event.get('tag'))
    
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
    
    return {
        'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
        'body': json.dumps({
            'message': plaintext_message.decode('utf-8')
        })
    }
