import json
import boto3
import base64
from botocore.exceptions import ClientError
import os

kms_client = boto3.client('kms')

def lambda_handler(event, context):
    message = event['message']  # The original message
    signature_b64 = event['signature']  # The base64 encoded signature

    ecc_kms_key_id = os.environ['ECC384_KMS_KEY_ARN']

    # Decode the signature from base64
    signature = base64.b64decode(signature_b64)

    try:
        # Verify the signature
        response = kms_client.verify(
            KeyId=ecc_kms_key_id,
            Message=message.encode('utf-8'),
            MessageType='RAW',
            Signature=signature,
            SigningAlgorithm='ECDSA_SHA_384'  # Use 'ECDSA_SHA_384' for P-384
        )
        
        return {
            'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({'verified': response['SignatureValid']})
        }
    except ClientError as e:
        return {
            'statusCode': e.response['ResponseMetadata']['HTTPStatusCode'],
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({'error': str(e)})
        }
