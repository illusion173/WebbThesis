#!/usr/bin/env python3
import boto3
import base64
import json
import os
import sys

# Initialize the boto3 client for KMS
kms_client = boto3.client('kms')

SIGN_ALGORITHM = 'HMAC_SHA_256'

def main():
# Read JSON input from stdin
    input_data = sys.stdin.read()

# Parse the JSON input
    data = json.loads(input_data)

    # Extract the message from the event payload
    message = data.get('message')

    sha_kms_key_id = os.environ['SHA256_KMS_KEY_ARN']

    # Convert the message to bytes
    message_bytes = message.encode('utf-8')
    # Use KMS to generate (HMAC) the message
    response = kms_client.generate_mac(
        KeyId=sha_kms_key_id,
        Message=message_bytes,
        SigningAlgorithm=SIGN_ALGORITHM
    )

    # Base64 encode the signature for output
    signature = base64.b64encode(response['Mac']).decode('utf-8')
    result_dict = {
        "signature" : signature
    }

    print(json.dumps(result_dict))

if __name__ == "__main__":
    main()
