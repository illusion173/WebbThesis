#!/usr/bin/env python3
import json
import boto3
import base64
from botocore.exceptions import ClientError
import os
import sys

# Initialize the KMS client
kms_client = boto3.client('kms')

def main():
# Read JSON input from stdin
    input_data = sys.stdin.read()

# Parse the JSON input
    data = json.loads(input_data)

    # Extract the message from the event payload
    message = data.get('message')

    ecc_kms_key_id = os.environ['ECC256_KMS_KEY_ARN']
    # Sign the message
    response = kms_client.sign(
        KeyId=ecc_kms_key_id,
        Message=message.encode('utf-8'),
        MessageType='RAW',
        SigningAlgorithm='ECDSA_SHA_256'  # Use 'ECDSA_SHA_384' for P-384
    )
    
    signature = response['Signature']

    # Encode the signature to base64 for easier transport
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    print(json.dumps({'signature': signature_b64}))

if __name__ == "__main__":
    main()
