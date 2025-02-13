import json
import boto3
import base64
from botocore.exceptions import ClientError
import os
# Initialize the KMS client
kms_client = boto3.client('kms')

def lambda_handler(event, context):

    body = json.loads(event["body"])
    message = body['message']  # The message to sign

    ecc_kms_key_id = os.environ['ECC256_KMS_KEY_ARN']
    try:
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

        return {
            'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({'signature': signature_b64})
        }

    except ClientError as e:
        return {
            'statusCode': e.response['ResponseMetadata']['HTTPStatusCode'],
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({'error': str(e)})
        }
