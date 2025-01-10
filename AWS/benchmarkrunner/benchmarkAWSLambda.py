import boto3
import time
import json
import requests
import re
from datetime import datetime, timezone
import pandas as pd

# Initialize a boto3 client for CloudWatch Logs
cloudwatch_logs_client = boto3.client('logs', region_name='us-east-1')  # Specify the correct region
save_file_name = "AWSLambdaBenchmarkResults.csv"
start_end_benchmark_times = []

def save_lambda_reports_to_csv(lambda_reports: dict, start_option: str)-> None:

    data_rows = []
    # essentially, key will be the cloudwatch log group, then a list of the reports (dictionaries)
    for cloudwatch_log_group_name, reports in lambda_reports.items():
        # /aws/lambda/ Remove this part
        main_info_string = cloudwatch_log_group_name.replace("/aws/lambda/", "")

        main_components_info = main_info_string.split("-")

        architecture = main_components_info[0]

        # convert sharp to # for languages
        language = main_components_info[1].replace("sharp", "#")
        operation = main_components_info[2]
        memory_size = main_components_info[3]
        # Kind of redundant to do this but thats alright just specify
        for report in reports:
            data_row = {
                "architecture": architecture,
                "start_type" : start_option,
                "operation" :operation,
                "language": language,
                "memory_size": memory_size,
                "execution_time_ms" : report.get("Duration"),
                "max_memory_usage_mb" : report.get("MaxMemoryUsed"),
                "init_duration_ms" : report.get("InitDuration"),
                "billed_duration_ms" : report.get("BilledDuration")
                }
            data_rows.append(data_row)

    df = pd.DataFrame(data_rows)


    # Write the DataFrame to a CSV file
    csv_file_path = f"./Lambda-Benchmark-Results-x86-{start_option}-rust-python-typescript.csv"
    df.to_csv(csv_file_path, index=False, mode='a')  # Set index=False to avoid writing row indices

def get_lambda_reports(start_end_benchmark_times: list[dict[str, list]]) -> dict[str, list]:
    """
    Retrieves Lambda reports from CloudWatch log groups within specified time ranges.

    :param start_end_benchmark_times: List of dictionaries with log group as the key and [start_time, end_time] as the value.
    :return: A dictionary with log group names as keys and a list of Lambda report dictionaries as values.
    """
    logs_client = boto3.client('logs')
    lambda_reports = {}

    # Regex to extract fields from the Lambda REPORT log lines
    report_regex = re.compile(
        r"REPORT RequestId: (?P<RequestId>[a-z0-9\-]+)\s+"
        r"Duration: (?P<Duration>[\d.]+) ms\s+"
        r"Billed Duration: (?P<BilledDuration>\d+) ms\s+"
        r"Memory Size: (?P<MemorySize>\d+) MB\s+"
        r"Max Memory Used: (?P<MaxMemoryUsed>\d+) MB\s+"
        r"(Init Duration: (?P<InitDuration>[\d.]+) ms\s+)?"
    )

    for benchmark in start_end_benchmark_times:
        for log_group, times in benchmark.items():
            start_time = times[0]
            end_time = times[1]
            reports_for_log_group = []

            # Get log streams for the log group
            log_streams = logs_client.describe_log_streams(
                logGroupName=log_group,
                orderBy='LastEventTime',
                descending=True
            ).get('logStreams', [])

            for stream in log_streams:
                log_stream_name = stream['logStreamName']

                # Get log events for the log stream within the time range
                events = logs_client.get_log_events(
                    logGroupName=log_group,
                    logStreamName=log_stream_name,
                    startTime=start_time,
                    endTime=end_time,
                    startFromHead=True
                ).get('events', [])

                for event in events:
                    message = event['message']
                    match = report_regex.search(message)

                    if match:
                        report = {}
                        # Extract fields and add to the reports list
                        groupedReport = match.groupdict()
                        # Convert numeric fields to appropriate types
                        report['Duration'] = float(groupedReport['Duration'])
                        report['BilledDuration'] = int(groupedReport['BilledDuration'])
                        report['MemorySize'] = int(groupedReport['MemorySize'])
                        report['MaxMemoryUsed'] = int(groupedReport['MaxMemoryUsed'])
                        if groupedReport['InitDuration'] is not None:
                            report['InitDuration'] = float(groupedReport['InitDuration'])
                        else:
                            report['InitDuration'] = float(0.0)
                        reports_for_log_group.append(report)

                lambda_reports[log_group] = reports_for_log_group

    return lambda_reports

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

        input_data_loc = f"../../TestArtifacts/AWS/inputs/{operation}.json"
        with open(input_data_loc, 'r') as file:
            test_case_inputs[operation] = json.load(file)

    return test_case_inputs

# build the key lookup dictionary for getting lambda api urls.
# value is string api_url
def get_lambda_api_urls() -> dict[str,str]:

    # Initialize an empty dictionary to store API URLs
    lambda_api_urls = {}

    # Read the JSON file
    with open("./lambda_benchmark_urls.json") as file:
        # Load the JSON content
        lambda_api_urls = json.load(file)

    if lambda_api_urls is None:
        print("No Lambda api urls loaded?")
        print("File should be in location ../iac-microbenchmark/lambda_benchmark_urls.json")
        exit(1)

    return lambda_api_urls

def create_tc(start_option: str, operation: str, language: str, lambda_url: str, test_case_input: dict[str,str], correct_answer: dict[str,str], iterations: int, arch_dir: str, memory_size: int)-> dict:

    # Clean in case of c# -> csharp
    cleanedLang = language.replace("#","sharp")

    cloudwatch_group_name = f"/aws/lambda/{arch_dir}-{cleanedLang}-{operation}-{memory_size}"
    # Build the test case
    test_case = {
        "operation_input": test_case_input,
        "validation": correct_answer,
        "start_type": start_option,
        "iterations": iterations,
        "operation" : operation,
        "language" : language,
        "lambda_url" : lambda_url,
        "cloudwatch_log_group" :  cloudwatch_group_name,
        "architecture": arch_dir,
        "memory": memory_size
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


def ensure_https(url):
    if not url.startswith("https://"):
        url = "https://" + url
    return url

def execute_tc(test_case: dict):

    # Extract the lambda URL from the dictionary
    lambda_url = test_case.get("lambda_url")
    payload_body = test_case.get("operation_input")
    iterations = test_case.get("iterations")
    test_case_log_group = test_case.get("cloudwatch_log_group")
    test_case_langauge = test_case.get("language")
    
    if not lambda_url:
        raise ValueError("Missing 'lambda_url' in test case dictionary")

    if not payload_body:
        raise ValueError("Missing 'operation_input' in test case dictionary")

    if not iterations:
        raise ValueError("Missing 'iterations' in test case dictionary")

    lambda_url = ensure_https(lambda_url)

    # Check if we need to do a warm-up, execute the operations 10 times to warm up
    if test_case["start_type"] == "warm":

        for _ in range(0,10):
            execute_warmup(lambda_url, payload_body)    

    # Need to fix this later, this is to fix serialization issues
    if test_case_langauge == "c#":
        input = convert_dict_keys(payload_body)
        payload_body = input

    # Get the current UTC time
    start_formatted_time = int(datetime.now(timezone.utc).timestamp() * 1000) - 2000 # add two second buffer

    request_headers = {"Content-Type": "application/json"}
    for _ in range(0,iterations):
        try:
            # Perform an HTTP POST request
            response = requests.post(lambda_url, json=payload_body, headers=request_headers)
            
            response.raise_for_status()  # Raise an error for any 4xx/5xx status codes

        except requests.exceptions.RequestException as e:
                print(f"HTTP Request failed: {e}")
                print(f"Test Case: \n")
                print(f"{test_case}")
                time.sleep(10)
                print("wait a second to test it again")

    # Once we are all done with the benchmarks
    # Format the time as 'YYYY-MM-DDTHH:MM:SS.sssZ'
    end_formatted_time = int(datetime.now(timezone.utc).timestamp() * 1000) + 2000 # add two second buffer
    start_end_benchmark_time = {}

    # Key will be the log group, values are the start and end times of executing the test cases in str
    start_end_benchmark_time[test_case_log_group] = [start_formatted_time, end_formatted_time]

    start_end_benchmark_times.append(start_end_benchmark_time)

def convert_dict_keys(input_dict):
    # Create a new dictionary with transformed keys
    return {to_pascal_case(key): value for key, value in input_dict.items()}

def to_pascal_case(snake_str):
    # Convert snake_case to PascalCase
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def main():
    print("Beginning Initialization of AWS Lambda Benchmark runner")

    architectures = [
        "x86",
        #"arm"
    ]

    languages = [
        #'c#',
        #'go',
        'java',
        #'python', # Python is fully operational, for all combos.
        #'rust', # Rust is fully operational, for all combos
        #'typescript', # Typescript is fully operational, for all combos.
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

    #Must comment out which one to test.
    # comment out cold to do warm testing, vice versa.
    start_options = [
        "cold",
        #"warm"
    ]

    # All in MB
    memory_sizes = [
        #128,
        #512,
        #1024,
        #1769,
        3008
    ]

    # Key is operation, value is json containing answers
    #correct_answers = get_correct_answers(operations)
    correct_answers = {}
    print("Succesful loading of correct answers")

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    print("Succesful loading of operation inputs")

    # Grab appropriate urls for lambda calls
    # value is string api_url
    operation_urls = get_lambda_api_urls()
    print("Succesful Loading of AWS Lambda URLs")

    test_cases = []
    iterations = 1

    # First we need to create the testcases themselves
    for language in languages:
        for operation in operations:
            for start_option in start_options:
                for memory_size in memory_sizes:
                    for architecture in architectures:  

                        # first we need to grab the api_url for the test case
                        # remember to clean the lang for c# -> csharp
                        sanitizedLang = language.replace("#","sharp")
                        api_url_key = f"{architecture}-{sanitizedLang}-{operation}-{memory_size}"

                        # Retrieve the api url
                        test_case_lambda_api_url = operation_urls.get(api_url_key)

                        if test_case_lambda_api_url == None:
                            print("")
                            print("")
                            print("")
                            print("")
                            print("ERROR!!")
                            print("No API URL for operation error.")
                            print("Check the following api url key in json:")
                            print(f"{api_url_key}")
                            exit(1)

                        test_case_input = test_case_inputs[operation]
                        correct_answer_input  = correct_answers.get(operation, "")

                        # Then Create the test case
                        new_test_case = create_tc(start_option,operation,language,test_case_lambda_api_url,test_case_input,correct_answer_input,iterations,architecture,memory_size)

                        test_cases.append(new_test_case)

    print("Finished Initialization of AWS Lambda Benchmark Runner")
    print("EXECUTE")

    # Then execute the test cases, http requests
    num_of_test_cases = len(test_cases)
    for test_case in test_cases:

        print("---------------------------------------")
        print(f"Executing Test Case")
        #print(f">Operation: {test_case["operation"]}
        print(f"Operation")
        test_case_op = test_case["operation"]
        test_case_lang = test_case["language"]
        test_case_start = test_case["start_type"]
        test_case_arch = test_case["architecture"]
        test_case_mem = test_case["memory"]

        print(f">Operation: {test_case_op}")
        print(f">Language: {test_case_lang}")
        print(f">Start Type: {test_case_start}")
        print(f">Architecture:{test_case_arch} ")
        print(f">Memory Size: {test_case_mem}")


        # Execute Test Case
        execute_tc(test_case)
        num_of_test_cases -= 1
        print(f"Number of test cases left: {num_of_test_cases}")
        print("---------------------------------------")
        print("")

        # Sleep for some time before moving on to next test case to settle
        time.sleep(0.1)

    print("-" * 10)
    print("-" * 10)
    print("Waiting for Cloudwatch to settle, lambda operations may take a minute to fully report.")
    print("Begin wait for 120 seconds.")
    print("-" * 10)
    print("-" * 10)

    # wait for 120 seconds
    time.sleep(120)

    print("Finished waiting 120 seconds.")

    print("Begin Saving Results from benchmark.")

    lambda_reports = get_lambda_reports(start_end_benchmark_times)

    save_lambda_reports_to_csv(lambda_reports, start_options[0])

    print("Finished saving results from benchmark.")

    print("Finished AWS Lambda Benchmark Runner")
    time.sleep(15000)
    exit(0)

if __name__ == "__main__":
    main()
