import boto3
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

kms_client = boto3.client('kms')

def lambda_handler(event, context):
    # Get public key from AWS KMS
    key_id = 'alias/example-rsa-key'
    public_key_response = kms_client.get_public_key(KeyId=key_id)
    
    public_key_der = public_key_response['PublicKey']
    public_key = serialization.load_der_public_key(public_key_der, backend=default_backend())
    
    # Generate random 256-bit AES key
    aes_key = os.urandom(32)  # 32 bytes = 256 bits
    
    # Encrypt the payload with AES-256 CTR
    payload = event['payload'].encode('utf-8')
    iv = os.urandom(16)  # Random initialization vector for AES-CTR
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_payload = encryptor.update(payload) + encryptor.finalize()
    
    # Encrypt the AES key using the RSA public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Return encrypted payload and encrypted AES key
    return {
        'encrypted_payload': encrypted_payload.hex(),
        'encrypted_aes_key': encrypted_aes_key.hex(),
        'iv': iv.hex()
    }
