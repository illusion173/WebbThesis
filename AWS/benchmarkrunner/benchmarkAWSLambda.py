import boto3
import time
import json
import requests
import platform
import subprocess
import psutil
from botocore.exceptions import ClientError
import uuid

# Initialize a boto3 client for CloudWatch Logs
cloudwatch_logs_client = boto3.client('logs', region_name='us-east-1')  # Specify the correct region
log_group_name = "WebbBenchmark"

def get_correct_answers(operations: list) -> dict:
    correct_answers = {}

    # Prepend the directory to each operation and store in the dictionary
    for operation in operations:
        correct_answer_loc = f"../../TestArtifacts/correct/{operation}.json"
        with open(correct_answer_loc, 'r') as file:
            correct_answers[operation] = json.load(file)

    return correct_answers

def get_testcase_inputs(operations: list) -> dict:
    test_case_inputs = {}

    for operation in operations:
        input_data_loc = f"../../TestArtifacts/inputs/{operation}.json"
        with open(input_data_loc, 'r') as file:
            test_case_inputs[operation] = file.read()

    return test_case_inputs


def get_lambda_api_urls(architectures: list, languages: list, operations: list) -> dict:

    return {}


def create_tc():


    return {}

def execute_warmup():

    return {}

def execute_tc():

    return {}

def determine_result():

    return True



def main():
    print("Finished Initialization of AWS Lambda Benchmark runner")
    # Each Lambda function will have a unique url to ping
    operation_urls = {}

    architectures = [
        "x86",
        "arm"
    ]

    languages = [
        'c#',
        'go',
        'java',
        'python',
        'rust',
        'typescript',
    ]

    operations = [
    'aes256_decrypt',
    'aes256_encrypt',
    'ecc256_sign',
    'ecc256_verify',
    'ecc384_sign',
    'ecc384_verify',
    'rsa2048_decrypt',
    'rsa2048_encrypt',
    'rsa3072_decrypt',
    'rsa3072_encrypt',
    'rsa4096_decrypt',
    'rsa4096_encrypt',
    'sha256',
    'sha384',
    ]

    #for cold_start
    start_options = [
        "cold",
        "warm"
    ]

    # Grab appropriate urls
    operation_urls = get_lambda_api_urls(architectures, languages, operations)

    # Key is operation, value is json containing answers
    correct_answers = get_correct_answers(operations)
    print("Succesful loading of correct answers")

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    print("Succesful loading of operation inputs")




if __name__ == "__main__":
    print("Begin Initialization of AWS Lambda Benchmark runner")
    main()
