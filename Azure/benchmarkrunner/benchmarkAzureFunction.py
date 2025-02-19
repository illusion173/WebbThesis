import time
import json
import requests
from datetime import datetime, timezone

def get_correct_answers(operations: list) -> dict:
    correct_answers = {}

    '''
    # Prepend the directory to each operation and store in the dictionary
    for operation in operations:
        correct_answer_loc = f"../../TestArtifacts/Azure/correct/{operation}.json"
        with open(correct_answer_loc, 'r') as file:
            correct_answers[operation] = json.load(file)
    '''
    

    return correct_answers

def get_testcase_inputs(operations: list) -> dict:
    test_case_inputs = {}

    for operation in operations:
        input_data_loc = f"../../TestArtifacts/Azure/inputs/{operation}.json"
        try:
            # Open and load the JSON content
            with open(input_data_loc, 'r') as file:
                test_case_inputs[operation] = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found - {input_data_loc}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {input_data_loc}: {e}")

    return test_case_inputs

# build the key lookup dictionary for getting af api urls.
# value is string api_url
def get_azure_func_api_urls() -> dict[str,str]:

    # Initialize an empty dictionary to store API URLs
    azure_api_urls = {}

    # Read the JSON file
    with open("./function_urls.json") as file:
        # Load the JSON content
        azure_api_urls = json.load(file)

    if azure_api_urls is None:
        print("No Azure api urls loaded?")
        exit(1)

    return azure_api_urls

def execute_warmup(azure_url: str, payload_body: str) -> None:

    try:
        request_headers = {"Content-Type": "application/json"}
        # Perform an HTTP POST request
        response = requests.post(azure_url, json=payload_body, headers=request_headers)

        response.raise_for_status()  # Raise an error for any 4xx/5xx status codes
        
        return None
    
    except requests.exceptions.RequestException as e:

        print(f"HTTP Request failed: {e}")
        exit(1)



def create_tc(start_option: str, operation: str, language: str, azure_url: str, test_case_input: dict[str,str], correct_answer: dict[str,str], iterations: int, arch_dir: str)-> dict:

    # Clean in case of c# -> csharp
    operationName = ""
    if language == "c#":
        operationName = f"dotnet_{operation}_program"

    operationName = f"{language}_{operation}"
    # Build the test case
    test_case = {
        "operation_input": test_case_input,
        "validation": correct_answer,
        "start_type": start_option,
        "iterations": iterations,
        "operation" : operation,
        "language" : language,
        "azure_url" : azure_url,
        "architecture": arch_dir,
        "operationName" : operationName
    }

    return test_case

def execute_tc(test_case: dict):

    # Extract the lambda URL from the dictionary
    azure_url = test_case.get("azure_url")
    payload_body = test_case.get("operation_input")
    iterations = test_case.get("iterations")
    
    start_end_benchmark_times={}
    if not azure_url:
        raise ValueError("Missing 'azure_url' in test case dictionary")

    if not payload_body:
        raise ValueError("Missing 'operation_input' in test case dictionary")

    if not iterations:
        raise ValueError("Missing 'iterations' in test case dictionary")

    # Check if we need to do a warm-up, execute the operations 10 times to warm up
    if test_case["start_type"] == "warm":

        print("Begin Warmup")
        for _ in range(0,10):
            execute_warmup(azure_url, payload_body)    

        print("Finished Warmup")
        print("Begin sleeping 3 seconds for settling")
        time.sleep(3)
        print("finish waiting")    # Get the current UTC time

    start_formatted_time = int(datetime.now(timezone.utc).timestamp() * 1000) - 2000 # add two second buffer
    timestamp_sec = start_formatted_time / 1000.0

    # Convert to datetime
    dt = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)

    # Format as KQL datetime format
    start_kql_datetime = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    request_headers = {"Content-Type": "application/json"}
    for i in range(0,iterations):
        print(i)
        try:
            # Perform an HTTP POST request
            response = requests.post(azure_url, json=payload_body, headers=request_headers)
            
            response.raise_for_status()  # Raise an error for any 4xx/5xx status codes

        except requests.exceptions.RequestException as e:
                print(f"HTTP Request failed: {e}")
                print(f"Test Case: \n")
                print(f"{test_case}")
                time.sleep(10)
                print("wait a second to test it again")


    end_formatted_time = int(datetime.now(timezone.utc).timestamp() * 1000) + 2000 # add two second buffer
    end_timestamp_sec = end_formatted_time / 1000.0

    # Convert to datetime
    end_dt = datetime.fromtimestamp(end_timestamp_sec, tz=timezone.utc)

    # Format as KQL datetime format
    end_kql_datetime = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_end_benchmark_times["benchmarktimes"] = [start_kql_datetime, end_kql_datetime]

    test_case.update(start_end_benchmark_times)
    return test_case

def main():

    languages = [
        'c#',
        'java',
        'python',
        'typescript',
    ]

    operations = [
        'ecc256_sign', # works for all
        'ecc256_verify', # works for all
        'ecc384_sign', # works for all
        'ecc384_verify', # works for all
        'rsa2048_decrypt', # works for all
        'rsa2048_encrypt', # works for all
        'rsa3072_decrypt', # works for all
        'rsa3072_encrypt', # works for all
        'rsa4096_decrypt', # works for all
        'rsa4096_encrypt', # works for all
    ]

    #for cold_start
    start_options = [
        "cold",
        #"warm"
    ]

    # Key is operation, value is json containing answers
    #correct_answers = get_correct_answers(operations)
    print("Succesful loading of correct answers")

    # Key is operation, value is json containing inputs
    test_case_inputs = get_testcase_inputs(operations)
    print("Succesful loading of operation inputs")

    operation_urls = get_azure_func_api_urls()

    test_cases = []
    iterations = 30
    arch_dir = "x86"

    # To save the results
    save_result_file_name = f"./{start_options[0]}-azurefunc-BenchmarkTimes.json"

    finished_test_cases = []

    # First we need to create the testcases themselves
    for language in languages:
        for operation in operations:
            for start_option in start_options:
                # Get operation's input
                test_case_input = test_case_inputs[operation]
                # Clean in case of c# -> csharp
                operationName = ""

                if language == "c#":
                    operationName = f"dotnet_{operation}_program"
                else:
                    operationName = f"{language}_{operation}"

                azure_url = operation_urls[operationName]

                # get operation's correct_answer
                #correct_answer = correct_answers[operation]
                
                new_test_case = create_tc(start_option,operation,language,azure_url,test_case_input,{},iterations,arch_dir)

                test_cases.append(new_test_case)

    # Then execute the test cases, http requests
    num_of_test_cases = len(test_cases)
    for test_case in test_cases:

        test_case_op = test_case["operation"]
        test_case_lang = test_case["language"]
        test_case_start = test_case["start_type"]
        test_case_arch = test_case["architecture"]


        print("---------------------------------------")
        print(f"Executing Test Case")
        print(f">Operation: {test_case_op}")
        print(f">Language: {test_case_lang}")
        print(f">Start Type: {test_case_start}")
        print(f">Architecture:{test_case_arch} ")

        # Execute Test Case
        finished_test_case = execute_tc(test_case)

        finished_test_cases.append(finished_test_case)

        num_of_test_cases -= 1

        print(f"Number of test cases left: {num_of_test_cases}")
        print("---------------------------------------")
        print("")

        # Sleep for some time before moving on to next test case to settle
        time.sleep(0.1)

    print("-" * 10)
    print("-" * 10)
    print("-" * 10)
    print("-" * 10)


    # Write the list of JSON objects to the file
    with open(save_result_file_name, 'w') as json_file:
        json.dump(test_cases, json_file, indent=4)  # 'indent=4' for pretty printing

    print(f"Data has been written to {save_result_file_name}")


if __name__ == "__main__":
    main()
