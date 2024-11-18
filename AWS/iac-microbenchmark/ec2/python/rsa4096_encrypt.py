import base64
import json
import os
import sys
import secrets
import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Initialize AWS KMS client
kms_client = boto3.client('kms')

def main():
    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)

    # Extract the message from the input payload
    message = request_json.get('message')

    # Get the KMS key ID from environment variables
    rsa_kms_key_id = os.environ['RSA4096_KMS_KEY_ARN']

    # Generate a random AES key and IV
    aes_key = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)

    # Encrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    plaintext = message.encode('utf-8')
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Encrypt the AES key using KMS
    response = kms_client.encrypt(
        KeyId=rsa_kms_key_id,
        Plaintext=aes_key,
        EncryptionAlgorithm="RSAES_OAEP_SHA_256"
    )
    encrypted_aes_key = response['CiphertextBlob']

    # Return the results
    result = {
        'iv': base64.b64encode(iv).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8')
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
