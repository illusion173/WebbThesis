import base64
import json
import os
import sys
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# AWS KMS Client
kms_client = boto3.client('kms')

def main():
    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)
    # Get the KMS key ID from environment variables
    rsa_kms_key_id = os.environ['RSA3072_KMS_KEY_ARN']
    
    # Get the data from the input payload
    encrypted_aes_key_b64 = request_json.get('encrypted_aes_key')
    iv_b64 = request_json.get('iv')
    ciphertext_b64 = request_json.get('ciphertext')

    # Decode base64 values
    encrypted_aes_key = base64.b64decode(encrypted_aes_key_b64)
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    # Decrypt the AES key using KMS
    response = kms_client.decrypt(
        CiphertextBlob=encrypted_aes_key,
        KeyId=rsa_kms_key_id,
        EncryptionAlgorithm="RSAES_OAEP_SHA_256"
    )
    aes_key = response['Plaintext']

    # Decrypt the data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Return the plaintext as a JSON response
    result = {
        'plaintext': plaintext.decode('utf-8')
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
