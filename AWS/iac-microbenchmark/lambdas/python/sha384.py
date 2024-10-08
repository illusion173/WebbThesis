import boto3
import base64
import json
import os

# Initialize the boto3 client for KMS
kms_client = boto3.client('kms')

SIGN_ALGORITHM = 'HMAC_SHA_384'

def lambda_handler(event, context):

    # Extract the message from the event payload
    message = event.get('message')

    sha_kms_key_id = os.environ['SHA384_KMS_KEY_ARN']

    # Convert the message to bytes
    message_bytes = message.encode('utf-8')

    try:
        # Use KMS to sign (HMAC) the message
        response = kms_client.generate_mac(
            KeyId=sha_kms_key_id,
            Message=message_bytes,
            SigningAlgorithm=SIGN_ALGORITHM
        )
        # Base64 encode the signature for output
        signature = base64.b64encode(response['Mac']).decode('utf-8')
        return {
            'statusCode': 200,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({
                'signature': signature
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
        'headers' : {"Access-Control-Allow-Origin": "*",
                     "content-type": "application/json"},
            'body': json.dumps({'error': str(e)})
        }
