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

    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)

    message = request_json["message"]

    sha_kms_key_id = os.environ['SHA256_KMS_KEY_ARN']

    # Convert the message to bytes
    message_bytes = message.encode('utf-8')
    # Use KMS to generate (HMAC) the message
    response = kms_client.generate_mac(
        KeyId=sha_kms_key_id,
        Message=message_bytes,
        MacAlgorithm=SIGN_ALGORITHM
    )

    # Base64 encode the signature for output
    signature = base64.b64encode(response['Mac']).decode('utf-8')
    result_dict = {
        "signature" : signature
    }

    print(json.dumps(result_dict))

if __name__ == "__main__":
    main()
