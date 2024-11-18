import json
import boto3
import base64
from botocore.exceptions import ClientError
import os
import sys
import json

kms_client = boto3.client('kms')

def main():
    # Get the name argument from sys.argv
    request_json_raw = sys.argv[1]

    request_json = json.loads(request_json_raw)
    # Extract the message from the event payload
    message = request_json.get('message')

    signature_b64 = request_json.get('signature')

    signature = base64.b64decode(signature_b64)

    ecc_kms_key_id = os.environ['ECC256_KMS_KEY_ARN']
     # Verify the signature
    response = kms_client.verify(
        KeyId=ecc_kms_key_id,
        Message=message.encode('utf-8'),
        MessageType='RAW',
        Signature=signature,
        SigningAlgorithm='ECDSA_SHA_256'  # Use 'ECDSA_SHA_384' for P-384
    )
        
    print(json.dumps({'verified': response['SignatureValid']}))

if __name__ == "__main__":
    main()
