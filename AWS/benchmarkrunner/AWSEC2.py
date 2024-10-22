import boto3
import time
import json
import requests
import platform
import time
import random
import subprocess
import time
import psutil
import json
from botocore.exceptions import ClientError

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

def create_test_case_result(execution_time, ):

    return {}






# Record Test Case results
def post_tc_results(test_case_results: list, log_stream_name: str):

    events = []


    # Prepare the log event
    log_event = {
        'logGroupName': log_group_name,
        'logStreamName': log_stream_name,
        'logEvents': [
            {
                'timestamp': int(time.time() * 1000),  # Current time in milliseconds
                'message': json.dumps(test_case_results) 
            }
        ]
    }
  # Send the log event
    try:
        response = cloudwatch_logs_client.put_log_events(**log_event)
    except ClientError as e:
        print(f"Failed to post log: {e}")
    print("RECORDING TEST CASE RESULTS")

# Just checking if the received response from execution matches the correct answer struct    
def determine_result_tc(received_response: dict, correct_answer: dict):
    return received_response == correct_answer

def get_instance_type():
    try:
        # Querying the instance metadata service to get the instance type
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-type')
        if response.status_code == 200:
            return response.text
        else:
            return "Unable to retrieve instance type. Status code: {}".format(response.status_code)
    except requests.exceptions.RequestException as e:
        return "Error querying instance metadata: {}".format(e)

def create_tc(arch_dir: str, language: str, operation: str, input: dict, correct_answer: dict, start_type: str, instance_type: str, iterations: int)-> dict:
    test_case = {}

    command = ""
    file_loc = ""

    match language:
        case 'c#':
            command = ""
            print("You selected C#.")
        case 'go':
            print("You selected Go.")
        case 'java':
            print("You selected Java.")
        case 'python':
            # In the case of python, simply the location of the .py file
            command = "python3"
            file_loc = f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}.py"
            print("You selected Python.")
        case 'rust':
            print("You selected Rust.")
        case 'typescript':
            print("You selected TypeScript.")
        case _:
            print("Unknown language.")

    # Do the physical building of the test case here
    test_case["command"] = command
    test_case["file_loc"] = file_loc
    test_case["operation_input"] = input
    test_case["validation"] = correct_answer
    test_case["start_type"] = start_type
    log_stream_name = f"{instance_type}/{arch_dir}/{language}/{operation}/{start_type}"
    test_case["log_stream"] = log_stream_name
    test_case["iterations"] = iterations

    return test_case


def execute_test_case(test_case: dict):
    # Start the timer
    start_time = time.perf_counter()
    
    # Use subprocess to run the executable
    process = subprocess.Popen(
        [executable_command],
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )

    # Convert input data to JSON format
    json_input = json.dumps(input_data)

    # Send input data to the executable
    stdout, stderr = process.communicate(input=json_input.encode())
    
    # Get the process ID
    pid = process.pid
    
    # Wait for the process to complete
    process.wait()
    
    # Measure the end time
    end_time = time.perf_counter()
    
    # Measure memory usage
    mem_usage = psutil.Process(pid).memory_info().rss  # in bytes
    memory_usage_mb = mem_usage / (1024 ** 2)  # Convert to MB

    # Calculate execution time
    execution_time = end_time - start_time

    json_stdout = json.loads(stdout.decode())


    return None

def main():

    # Get Architecture
    architecture = platform.machine()

    if architecture == "x86_64":
        arch_dir = "x86"
    else:
        arch_dir = "arm"

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

    instance_type = get_instance_type()

    #print(f"Beginning AWS EC2 Benchmark runner for instance: {instance_type}")

    # Key is operation, value is json containing answers
    correct_answers = get_correct_answers(operations)

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    test_cases = []
    iterations = 50

    onekb = "../../TestArtifacts/1KB.txt"


    # First we need to create the testcases themselves
    for language in languages:
        for operation in operations:
            for start_option in start_options:
                # Get operation's input
                test_case_input = test_case_inputs[operation]

                # get operation's correct_answer
                correct_answer = correct_answers[operation]

                new_test_case = create_tc(arch_dir,language,operation, test_case_input,correct_answer,start_option, instance_type, iterations)

                test_cases.append(new_test_case)


    for test_case in test_cases:
        execute_test_case(test_case)


if __name__ == "__main__":
    print("Initialize AWS EC2 Benchmark runner")
    main()
