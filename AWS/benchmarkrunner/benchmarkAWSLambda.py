import boto3
import time
import json
import requests
import re
from datetime import datetime, timezone
import pandas as pd

# Initialize a boto3 client for CloudWatch Logs
cloudwatch_logs_client = boto3.client('logs', region_name='us-east-1')  # Specify the correct region
log_group_name = "WebbBenchmarkLambda"
save_file_name = "AWSLambdaBenchmarkResults.csv"
start_end_benchmark_times = []

def save_testcase_results(lambda_reports: list, file_name: str) -> None:
    """
    Save the test case results to a CSV file using pandas.
    """
    # List to hold all rows of data
    data_rows = []

    # Lambda reports is a list of dictionaries.
    # the key is the log stream name, the value is a list of dicts
    # the values are the dictionaries containing each report of the benchmark
    # the logstream name itself contains identifying information of the type of benchmark it was
    # report is this
    '''
    report = {
        "id": match.group("RequestId"),
        "duration": float(match.group("Duration")),
        "billedduration": float(match.group("BilledDuration")),
        "memorysize": int(match.group("MemorySize")),
        "maxmemoryused": int(match.group("MaxMemoryUsed")),
        "initduration": float(match.group("InitDuration")) if match.group("InitDuration") else None,
    }
    '''

    for item in lambda_reports:
        for log_stream_name, reports in item.items():
            values = log_stream_name.split("/")
            memory_size, arch_dir, language, operation, start_option = values
            for _, report in enumerate(reports):
                data_row = {
                    "architecture": arch_dir,
                    "start_type": start_option,
                    "operation": operation,
                    "language": language,
                    "memory_size" : memory_size
                }
                data_row.update(report)
                data_rows.append(data_row)
    
    # convert to pd dataframe
    df = pd.DataFrame(data_rows)
    
    # Save DataFrame to a CSV file
    try:
        df.to_csv(file_name, index=False)
        print(f"Results successfully saved to {file_name}")
    except Exception as e:
        print(f"Failed to save results: {e}")


def parse_report_line(report_line):
    """
    Parses a Lambda REPORT line into a dictionary with numeric values.

    Args:
        report_line (str): The REPORT line to parse.

    Returns:
        dict: A dictionary containing the parsed values.
    """
    report_pattern = re.compile(
        r"RequestId:\s+(?P<RequestId>[\w-]+).*?"  # RequestId
        r"Duration:\s+(?P<Duration>[\d.]+)\s+ms.*?"  # Duration
        r"Billed Duration:\s+(?P<BilledDuration>[\d.]+)\s+ms.*?"  # Billed Duration
        r"Memory Size:\s+(?P<MemorySize>[\d.]+)\s+MB.*?"  # Memory Size
        r"Max Memory Used:\s+(?P<MaxMemoryUsed>[\d.]+)\s+MB.*?"  # Max Memory Used
        r"(Init Duration:\s+(?P<InitDuration>[\d.]+)\s+ms)?"  # Init Duration (optional)
    )

    match = report_pattern.search(report_line)
    if not match:
        raise ValueError(f"Invalid REPORT line format: {report_line}")

    parsed_data = {
        "id": match.group("RequestId"),
        "duration": float(match.group("Duration")),
        "billedduration": float(match.group("BilledDuration")),
        "maxmemoryused": int(match.group("MaxMemoryUsed")),
        "initduration": float(match.group("InitDuration")) if match.group("InitDuration") else None,
    }

    return parsed_data


def get_lambda_reports(log_group_name, log_stream_names, start_time, end_time):
    """
    Fetches Lambda 'REPORT' log lines from specified CloudWatch log streams within a time range
    and parses them into dictionaries.

    Args:
        log_group_name (str): Name of the CloudWatch log group.
        log_stream_names (list): List of log stream names within the log group.
        start_time (str): Start time in ISO 8601 format ('YYYY-MM-DDTHH:MM:SS.sssZ').
        end_time (str): End time in ISO 8601 format ('YYYY-MM-DDTHH:MM:SS.sssZ').

    Returns:
        list: A list of parsed dictionaries containing 'REPORT' data.
    """
    # Convert ISO 8601 timestamps to milliseconds since epoch
    def iso_to_epoch_millis(iso_time):
        dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        return int(dt.timestamp() * 1000)

    logs_client = boto3.client("logs")

    # Convert timestamps to epoch milliseconds
    start_epoch = iso_to_epoch_millis(start_time)
    end_epoch = iso_to_epoch_millis(end_time)

    parsed_reports = []

    # Iterate over the specified log streams
    for log_stream_name in log_stream_names:
        # Filter log events for each log stream
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            logStreamNames=[log_stream_name],
            startTime=start_epoch,
            endTime=end_epoch,
            filterPattern="REPORT"
        )

        # Extract and parse the 'REPORT' log entries
        for event in response.get("events", []):
            message = event["message"]
            try:
                parsed_reports.append(parse_report_line(message))
            except ValueError as e:
                print(f"Skipping invalid REPORT line: {message}\nError: {e}")

    return parsed_reports




def get_correct_answers(operations: list[str]) -> dict:
    correct_answers = {}

    # Prepend the directory to each operation and store in the dictionary
    for operation in operations:
        correct_answer_loc = f"../../TestArtifacts/correct/{operation}.json"
        with open(correct_answer_loc, 'r') as file:
            correct_answers[operation] = json.load(file)

    return correct_answers

def get_testcase_inputs(operations: list[str]) -> dict:
    test_case_inputs = {}

    for operation in operations:
        input_data_loc = f"../../TestArtifacts/inputs/{operation}.json"
        with open(input_data_loc, 'r') as file:
            test_case_inputs[operation] = file.read()

    return test_case_inputs

# build the key lookup dictionary for getting lambda api urls.
# Key is a tuple (arch, language, operation, memory_size)
# value is string api_url
def get_lambda_api_urls() -> dict[tuple[str,str,str,int],str]:

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


def create_tc(start_option: str, operation: str, language: str, lambda_url: str, test_case_input: dict[str,str], correct_answer: dict[str,str], iterations: int, arch_dir: str, memory_size: int)-> dict:

    # Develop log stream name for filtering report in CloudWatch
    log_stream_name = f"{memory_size}/{arch_dir}/{language}/{operation}/{start_option}"

    # Build the test case
    test_case = {
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


    # Check if we need to do a warm-up, execute the operations 10 times to warm up
    if test_case["start_type"] == "warm":

        for _ in range(0,10):
            execute_warmup(lambda_url,payload_body)    

    # Get the current UTC time
    current_utc_time = datetime.now(timezone.utc)

    # Format the time as 'YYYY-MM-DDTHH:MM:SS.sssZ'
    start_formatted_time = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    # We need a way to filter the warmup logs with the real execution logs, do it by time
    test_case_log_stream = test_case.get("log_stream_name")

    for _ in range(0,iterations):
        try:
            # Perform an HTTP POST request
            response = requests.post(lambda_url, json=payload_body)

            response.raise_for_status()  # Raise an error for any 4xx/5xx status codes

            json_resp = response.json()

        except requests.exceptions.RequestException as e:
                print(f"HTTP Request failed: {e}")
                exit(1)

    # Once we are all done with the benchmarks
    # Get the current UTC time
    current_utc_time = datetime.now(timezone.utc)

    # Format the time as 'YYYY-MM-DDTHH:MM:SS.sssZ'
    end_formatted_time = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    start_end_benchmark_time = {}

    # Key will be the log stream, values are the start and end times of executing the test cases
    start_end_benchmark_time[test_case_log_stream] = [start_formatted_time, end_formatted_time]

    start_end_benchmark_times.append(start_end_benchmark_time)

def save_filter_times()->None:

    file_path = "lambda_filter_times.json"

    # Write the list of JSON objects to the file
    with open(file_path, 'w') as json_file:
        json.dump(start_end_benchmark_times, json_file, indent=4)

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

    # Grab appropriate urls for lambda calls
    # Key is a tuple (arch, language, operation, memory_size)
    # value is string api_url
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

                        key = (architecture, language, operation, memory_size)

                        # Retrieve the api url
                        test_case_lambda_api_url = operation_urls.get(key)

                        if test_case_lambda_api_url == None:
                            print("No API URL for operation?")
                            print(f"{key}")
                            exit(1)

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
        time.sleep(0.1)

    print("-" * 10)
    print("-" * 10)
    print("Waiting for Cloudwatch to settle, lambda operations may take 5-10 minutes to fully report.")
    print("-" * 10)
    print("-" * 10)

    time.sleep(60*10)

    lambda_reports = []

    print("Begin Saving Results from benchmark.")
    
    # Grab the results from AWS cloudwatch here
    for benchmark_time in start_end_benchmark_times:
        for log_stream, times in benchmark_time.items():
            start_time = times[0]
            end_time = times[1]

            # Obtain the physical result report
            reports = get_lambda_reports(log_group_name,log_stream,start_time,end_time)

            # Encompass report results
            lambda_reports[log_stream] = reports

    save_testcase_results(lambda_reports, save_file_name)

    print("Finished saving results from benchmark.")



    print("Finished AWS Lambda Benchmark Runner")
    exit(0)

if __name__ == "__main__":
    main()
