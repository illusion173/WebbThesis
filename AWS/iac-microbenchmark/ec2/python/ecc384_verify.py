#!/usr/bin/env python3
import json
import boto3
import base64
from botocore.exceptions import ClientError
import os
import sys
import json

kms_client = boto3.client('kms')

def main():
    # Read JSON input from stdin
    input_data = sys.stdin.read()
    # Parse the JSON input
    data = json.loads(input_data)

    # Extract the message from the event payload
    message = data.get('message')

    signature_b64 = data.get('signature')

    signature = base64.b64decode(signature_b64)

    ecc_kms_key_id = os.environ['ECC384_KMS_KEY_ARN']
     # Verify the signature
    response = kms_client.verify(
        KeyId=ecc_kms_key_id,
        Message=message.encode('utf-8'),
        MessageType='RAW',
        Signature=signature,
        SigningAlgorithm='ECDSA_SHA_384'  # Use 'ECDSA_SHA_384' for P-384
    )
        
    print(json.dumps({'verified': response['SignatureValid']}))

if __name__ == "__main__":
    main()
