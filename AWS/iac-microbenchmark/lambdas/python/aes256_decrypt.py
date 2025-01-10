import boto3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def lambda_handler(event, context):
    # Initialize KMS client
    kms_client = boto3.client('kms')
    
    body = json.loads(event["body"])

    # Extract the encrypted values from the request body
    encrypted_data_key_b64 = body.get('encrypted_data_key')
    iv_b64 = body.get('iv')
    tag_b64 = body.get('tag')
    encrypted_message_b64 = body.get('encrypted_message')

    # Check if all required values are provided
    if not all([encrypted_data_key_b64, iv_b64, tag_b64, encrypted_message_b64]):
        return {
            'statusCode': 400,
            'headers': {"Access-Control-Allow-Origin": "*", "content-type": "application/json"},
            'body': json.dumps({'error': 'Missing required encrypted data or parameters.'})
        }

    # Decode the base64-encoded values
    encrypted_data_key = base64.b64decode(encrypted_data_key_b64)
    iv = base64.b64decode(iv_b64)
    tag = base64.b64decode(tag_b64)
    ciphertext = base64.b64decode(encrypted_message_b64)
    
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
