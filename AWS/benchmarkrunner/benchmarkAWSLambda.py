import boto3
import time
import json
import requests
import platform
import subprocess
import psutil
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone

# Initialize a boto3 client for CloudWatch Logs
cloudwatch_logs_client = boto3.client('logs', region_name='us-east-1')  # Specify the correct region
log_group_name = "WebbBenchmarkLambda"
finished_warm_up_times = []

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

# Load the physical json file developed from the AWS CDK, return a dictionary for arch -> memory_size -> language -> memory_size
def get_lambda_api_urls():
    # Initialize an empty dictionary to store API URLs
    lambda_api_urls = {}

    # Read the JSON file
    with open("../iac-microbenchmark/lambda_benchmark_urls.json") as file:
        # Load the JSON content
        data = json.load(file)

    for entry in data:
        # Use a tuple of (architecture, language, operation, memory_size) as the key
        key = (entry['architecture'], entry['language'], entry['operation'], entry['memory_size'])
        # Store the corresponding 'api_url' in the dictionary
        lambda_api_urls[key] = entry['api_url']


    return lambda_api_urls

# Function to get the API URL using a specific key
def get_lambda_api_url(lambda_urls:dict , architecture: str, language: str, operation:str, memory_size:int):

    key = (architecture, language, operation, memory_size)

    return lambda_urls.get(key, "API URL not found")

def create_tc(start_option: str, operation: str, language: str, lambda_url: str, test_case_input: dict, correct_answer: dict, iterations: int, arch_dir: str, memory_size: int)-> dict:

    # Develop log stream name for filtering report in CloudWatch
    log_stream_name = f"{memory_size}/{arch_dir}/{language}/{operation}/{start_option}"


    # Build the test case
    test_case = {
        "id" : str(uuid.uuid4()), # generate a unique id for the test case
        "operation_input": test_case_input,
        "validation": correct_answer,
        "start_type": start_option,
        "iterations": iterations,
        "operation" : operation,
        "language" : language,
        "lambda_url" : lambda_url,
        "log_stream_name" :log_stream_name
    }

    return test_case

def execute_warmup(lambda_url: str, payload_body: str) -> None:

    try:
        # Perform an HTTP POST request
        response = requests.post(lambda_url, json=payload_body)

        response.raise_for_status()  # Raise an error for any 4xx/5xx status codes
        
        return None
    
    except requests.exceptions.RequestException as e:

        print(f"HTTP Request failed: {e}")
        exit(1)

def execute_tc(test_case: dict):

    # Extract the lambda URL from the dictionary
    lambda_url = test_case.get("lambda_url")
    payload_body = test_case.get("operation_input")
    iterations = test_case.get("iterations")
    
    if not lambda_url:
        raise ValueError("Missing 'lambda_url' in test case dictionary")

    if not payload_body:
        raise ValueError("Missing 'operation_input' in test case dictionary")

    if not iterations:
        raise ValueError("Missing 'iterations' in test case dictionary")


    # Check if we need to do a warm-up, execute the operations 50 times to warm up
    if test_case["start_type"] == "warm":

        for i in range(0,10):
            execute_warmup(lambda_url,payload_body)    

        # Get the current UTC time
        current_utc_time = datetime.now(timezone.utc)
        # Format the time as 'YYYY-MM-DDTHH:MM:SS.sssZ'
        formatted_time = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        # We need a way to filter the warmup logs with the real execution logs, do it by time
        test_case_log_stream = test_case["log_stream_name"]

        # Insert the test case operation,
        finished_warm_up_times.append({test_case_log_stream,formatted_time})

    for i in range(0,iterations):

        try:
            # Perform an HTTP POST request
            response = requests.post(lambda_url, json=payload_body)

            response.raise_for_status()  # Raise an error for any 4xx/5xx status codes

            json_resp = response.json()

        except requests.exceptions.RequestException as e:
                print(f"HTTP Request failed: {e}")
                exit(1)

def save_filter_times()->None:

    file_path = "lambda_filter_times.json"

    # Write the list of JSON objects to the file
    with open(file_path, 'w') as json_file:
        json.dump(finished_warm_up_times, json_file, indent=4)

    print(f"Data successfully saved to {file_path}")

    return None

def main():
    print("Beginning Initialization of AWS Lambda Benchmark runner")

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

    # All in MB
    memory_sizes = [
        128,
        256,
        512,
        1024,
        1536,
        2048
    ]

    # Key is operation, value is json containing answers
    correct_answers = get_correct_answers(operations)
    print("Succesful loading of correct answers")

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    print("Succesful loading of operation inputs")

    # Grab appropriate urls, key will be a tuple: 
    operation_urls = get_lambda_api_urls()
    print("Succesful Loading of AWS Lambda API GW URLs")

    test_cases = []
    iterations = 50

    # First we need to create the testcases themselves
    for language in languages:
        for operation in operations:
            for start_option in start_options:
                for memory_size in memory_sizes:
                    for architecture in architectures:  

                        # first we need to grab the api_url for the test case
                        test_case_lambda_api_url = get_lambda_api_url(operation_urls,architecture,language,operation,memory_size)
                        test_case_input = test_case_inputs[operation]
                        correct_answer_input = correct_answers[operation]

                        # Then Create the test case
                        new_test_case = create_tc(start_option,operation,language,test_case_lambda_api_url,test_case_input,correct_answer_input,iterations,architecture,memory_size)

                        test_cases.append(new_test_case)

    print("Finished Initialization of AWS Lambda Benchmark Runner")
    print("EXECUTE")

    # Then execute the test cases, http requests
    for test_case in test_cases:

        print("---------------------------------------")
        print(f"Executing Test Case")
        print(f">Operation: {test_case["operation"]}")
        print(f">Language: {test_case["language"]}")
        print(f">Start Type: {test_case["start_type"]}")

        # Execute Test Case
        execute_tc(test_case)
        print("---------------------------------------")
        print("")

        # Sleep for some time before moving on to next test case to settle
        time.sleep(0.05)

    print("Finished AWS Lambda Benchmark Runner")
    exit(0)



if __name__ == "__main__":
    main()
