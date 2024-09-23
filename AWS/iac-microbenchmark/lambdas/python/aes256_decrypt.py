import boto3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def lambda_handler(event, context):
    # Initialize KMS client
    kms_client = boto3.client('kms')
    
    # Get the KMS key ARN from environment variables
    # kms_key_id = os.environ['KMS_KEY_ARN']
    
    # Extract the encrypted data key and encrypted message from the event
    encrypted_data_key = base64.b64decode(event.get('encrypted_data_key'))
    encrypted_message = base64.b64decode(event.get('encrypted_message'))
    
    # Decrypt the data key using KMS
    response = kms_client.decrypt(
        CiphertextBlob=encrypted_data_key
    )

    plaintext_data_key = response['Plaintext']
    
    # Extract IV, tag, and ciphertext from the encrypted message
    iv = encrypted_message[:16]  # The first 16 bytes are the IV
    tag = encrypted_message[16:32]  # The next 16 bytes are the tag
    ciphertext = encrypted_message[32:]  # The rest is the ciphertext
    
    # Initialize decryption using AES-GCM
    cipher = Cipher(algorithms.AES(plaintext_data_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    
    # Decrypt the message
    padded_message = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding from the decrypted message
    unpadder = padding.PKCS7(16).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message.decode('utf-8')
        })
    }
