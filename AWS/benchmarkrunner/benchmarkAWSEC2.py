import boto3
import time
import json
import requests
import platform
import subprocess
import psutil
from botocore.exceptions import ClientError
import uuid
from datetime import datetime

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

# Record Test Case results
def post_tc_results(test_case_results: list, log_stream_name: str):

    events = []

    # Check if log stream exists
    try:
        response = cloudwatch_logs_client.describe_log_streams(
            logGroupName=log_group_name,
            logStreamNamePrefix=log_stream_name
        )
        log_streams = response['logStreams']
        
        # If the log stream doesn't exist, create it
        if not log_streams or not any(ls['logStreamName'] == log_stream_name for ls in log_streams):
            print(f"Log stream {log_stream_name} doesn't exist. Creating it.")
            cloudwatch_logs_client.create_log_stream(
                logGroupName=log_group_name,
                logStreamName=log_stream_name
            )
        else:
            print(f"Log stream {log_stream_name} already exists.")

    except ClientError as e:
        print(f"Error checking/creating log stream: {e}")
        return

    for test_case_result in test_case_results:
        log_event= {
                'timestamp': int(time.time() * 1000),  # Current time in milliseconds
                'message': json.dumps(test_case_result) 
        }
        events.append(log_event)

    # Prepare the log event
    log_event = {
        'logGroupName': log_group_name,
        'logStreamName': log_stream_name,
        'logEvents': events
    }

    # Send the log event
    try:
        response = cloudwatch_logs_client.put_log_events(**log_event)

    except ClientError as e:
        print(f"Failed to post log: {e}")

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
    # Mapping of language to command and file location format
    language_settings = {
        'c#': {"command": "", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}"},
        'go': {"command": "", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}"},
        'java': {"command": "", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}"},
        'python': {"command": "python3", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}.py"},
        'rust': {"command": "", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}"},
        'typescript': {"command": "node", "file_loc": f"../iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}.js"}
    }

    # Default values if language is unknown
    language_settings_default = {"command": "", "file_loc": ""}

    # Retrieve settings based on language, fallback to default if language is unknown
    settings = language_settings.get(language, language_settings_default)

    if settings["file_loc"] == "":
        print("ERROR FOR A TEST CASE, default entered?")
        print("No File Location for executable?")
        print(f"Operation: {operation}")
        print(f"Language: {language}")
        # EXIT FAILURE STOP BENCHMARK
        exit(1)

    # Develop log stream name for reporting in CloudWatch
    log_stream_name = f"{instance_type}/{arch_dir}/{language}/{operation}/{start_type}"

    # Build the test case
    test_case = {
        "id" : str(uuid.uuid4()), # generate a unique id for the test case
        "command": settings["command"],
        "file_loc": settings["file_loc"],
        "operation_input": input,
        "validation": correct_answer,
        "start_type": start_type,
        "log_stream_name": log_stream_name,
        "iterations": iterations,
        "operation" : operation,
        "language" : language,
        "architecture" : arch_dir
    }

    return test_case

def execute_warmup(subprocess_input):
    """Executes a warm-up operation using the provided subprocess input."""
    try:
        # Use subprocess to run the executable
        process = subprocess.Popen(
            subprocess_input,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for the process to complete
        process.wait()
        
    except Exception as e:
        print(f"Error during warm-up execution: {e}")

def execute_tc(test_case: dict):

    subprocess_input = []
    test_case_results = []

    # So input can be command, file loc, input
    # or for executables file_loc, input
    # This means that it is an executable
    if test_case["command"] == "":
        subprocess_input.append(test_case["file_loc"])
    else:
    # Python or javascript
        subprocess_input.append(test_case["command"])
        subprocess_input.append(test_case["file_loc"])

    # Always add input to the end as an arg
    subprocess_input.append(json.dumps(test_case["operation_input"]))

    # Retrieve how many times we need to run this test case
    num_iterations = test_case["iterations"]

    # Check if we need to do a warm-up, execute the operations 50 times to warm up
    if test_case["start_type"] == "warm":

        for i in range(0,10):
            execute_warmup(subprocess_input)
      
    for iteration in range(num_iterations):
        start_time = 0.0
        end_time = 0.0
        cpu_usage_samples = []  # to store CPU usage samples
        mem_usage_samples = [] # to store mem usage samples

        # Final result dict
        singular_test_case_result = {}

        # Start the timer
        start_time = time.perf_counter()
        
        # Use subprocess to run the operation
        process = subprocess.Popen(
            subprocess_input,
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        # Create a process object for tracking memory
        process_psutil = psutil.Process(process.pid)

        try:

            while process.poll() is None:  # While the script is still running

                # Update peak memory and CPU usage
                mem_usage_samples.append(process_psutil.memory_info().rss)
                
                cpu_usage_samples.append(process_psutil.cpu_percent(interval=0.01))  # interval of 0.1 sec for real-time updates

                time.sleep(0.01)  # Adjust this if needed to reduce CPU overhead

        except Exception as e:
            process.kill()
            raise e

        end_time = time.perf_counter()

        execution_time = end_time - start_time

        average_cpu_usage = sum(cpu_usage_samples) / len(cpu_usage_samples) if cpu_usage_samples else 0

        max_cpu_usage = max(cpu_usage_samples)

        average_mem_usage = sum(mem_usage_samples) / len(mem_usage_samples) if mem_usage_samples else 0

        max_mem = max(mem_usage_samples)

        stdout, stderr = process.communicate()

        # Grab the function's output for verification
        test_case_output = json.loads(stdout.decode())


        # Compile results in to dict
        singular_test_case_result["execution_time"] = execution_time * 1000 # Convert to ms
        singular_test_case_result["max_cpu_usage"] =  max_cpu_usage   # in % float
        singular_test_case_result["avg_cpu_usage"] =  average_cpu_usage   # in % float
        singular_test_case_result["max_memory_usage"] =  max_mem / (1024 ** 2)  # Convert to MB float float
        singular_test_case_result["avg_memory_usage"] =  average_mem_usage / (1024 ** 2)  # Convert to MB float
        #singular_test_case_result["successful"] = determine_result_tc(test_case_output,test_case["validation"]) # bool 
        singular_test_case_result["iteration"] = iteration # int
        singular_test_case_result["test_case_id"] = test_case["id"]

        test_case_results.append(singular_test_case_result)

    return test_case_results

def main():

    # Get Architecture
    architecture = platform.machine()

    instance_type = get_instance_type()

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

    # Key is operation, value is json containing answers
    correct_answers = get_correct_answers(operations)
    print("Succesful loading of correct answers")

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    print("Succesful loading of operation inputs")

    test_cases = []
    iterations = 100

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

    print("Finished Initialization")

    print("Beginning AWS EC2 Benchmark Runnner")

    print("EXECUTE")

    for test_case in test_cases:

        print("---------------------------------------")
        print(f"Executing Test Case")
        print(f">Operation: {test_case["operation"]}")
        print(f">Language: {test_case["language"]}")
        print(f">Start Type: {test_case["start_type"]}")

        # Execute Test Case
        test_case_result = execute_tc(test_case)
        log_stream_name = test_case["log_stream_name"]

        # After Test Case execution, post the results to cloudwatch logs
        post_tc_results(test_case_result, log_stream_name)
        print(f"Succesful Upload of test case results to log stream: {log_stream_name}")

        print("---------------------------------------")

        print("")
        # Sleep for a second before moving on to next test case to settle
        time.sleep(0.05)

    print("Finished AWS EC2 Benchmark Runner")
    print(f"Check selected Cloud Watch Log Group to view all data: {log_group_name}")
    exit(0)

if __name__ == "__main__":
    print("Begin Initialization of AWS EC2 Benchmark runner")
    main()
