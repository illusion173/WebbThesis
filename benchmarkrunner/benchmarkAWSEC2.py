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

def reportToCloudWatch(id: int, log_group:str, log_stream: str,  operation: str, architecture: str, execution_time: float,max_memory_used: float, instance_type: str, file_size_num: int, iteration: int):

    client = boto3.client('logs')

    try:
        # Code that might raise an exception
        client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
    except Exception as e:

        # Code that runs if the exception occurs
        print(f"Exception message: {e}")
        print("Log Stream may already exist.")

    # Log data
    timestamp = int(round(time.time() * 1000))  # CloudWatch needs timestamp in milliseconds
    #message = "Memory used: 512MB, Execution time: 2.5s"  # Your message
    message = { 'Id' : id,
               'Iteration': iteration,
               'MaxMemoryUsed' : max_memory_used, # in MB
               'Architecture' : architecture, # x86 or arm
               'Operation' : operation, # "aes256_encrypt"
               'ExecutionTime' : execution_time, # in ms
               'InstanceType' : instance_type, # m1.micro
                'FileSizeNum' : file_size_num
               }

    try:
        # Send log to CloudWatch Logs
        response = client.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[
                {
                    'timestamp': timestamp,
                    'message': json.dumps(message)
                }
            ]
        )
        print(response)

    except Exception as e:
        # Code that runs if the exception occurs
        print(f"Exception message: {e}")
        print("Error while inputting log event.")

def executeTestCase(executable, input_data: dict, )-> dict:
    # Start the timer
    start_time = time.perf_counter()
    
    # Use subprocess to run the executable
    process = subprocess.Popen(
        [executable],
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

    return {
        "TestCaseResult" : json_stdout,
        "MaxMemoryUsed":memory_usage_mb,
        "ExecutionTime":execution_time
    }

def load_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()  # Read the entire file content
    return content


def verifyTestCaseResponse(result, operation) -> bool:

    verify_file_loc = f"../test_artifacts/{operation}.json"
    # Open the JSON file and load the data
    with open(verify_file_loc, 'r') as file:
        verify_data = json.load(file)

    return result == verify_data

def main():

    # Get Architecture
    architecture = platform.machine()
    file_path = ["../test_artifacts/1KB.txt", "../test_artifacts/10KB.txt", "../test_artifacts/1MB.txt"]

    KbFile = load_text_file(file_path[0])
    TenKbFile = load_text_file(file_path[1])
    MbFile = load_text_file(file_path[2])

    test_case_text_list = []

    test_case_text_list.append(KbFile)
    test_case_text_list.append(TenKbFile)
    test_case_text_list.append(MbFile)

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
    # Testing Log group
    log_group = "/benchmark/Webb/Test"
    # Production Log group
    #log_group = "/benchmark/Webb/Prod"
    # For each language, an encryption will be ran, and for each test case, a different size of file (plaintext) will be read
    iterations = 100

    for start_option in start_options:
        for language in languages:
            for operation in operations:
                for index, test_case_text in enumerate(test_case_text_list):

                    test_case_id = random.randint(1, 9999999)

                    log_stream_name = f"{arch_dir}/{instance_type}/{operation}/{language}/{start_option}/{str(test_case_id)}"

                    match language:
                        case "java":
                            # Absolute path, kind of bad
                            test_case_executable_dir = f"../AWS/iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}-1.0-SNAPSHOT.jar"
                            match operation:
                                case "sha256":
                                    input_data = {"message": test_case_text}
                                    # We warm first by running a single test case
                                    if start_option == "warm":
                                        executeTestCase(test_case_executable_dir, input_data)

                                    for i in range(iterations):
                                        test_case_result = executeTestCase(test_case_executable_dir, input_data)
                                        if(verifyTestCaseResponse(test_case_result["TestCaseResult"],operation)):
                                            print("succeed")
                                            reportToCloudWatch(test_case_id,log_group,log_stream_name,operation,arch_dir,test_case_result["ExecutionTime"],test_case_result["MaxMemoryUsed"],instance_type,index, i)
                                        else:
                                            print("ERROR IN TESTCASE:")
                                            print(test_case_result)
                        case "c#":
                            print("Test")
                        case "go":
                            print("Test")
                        case "python":

                            test_case_executable_dir = f"../AWS/iac-microbenchmark/ec2/{language}/{operation}.py"
                            match operation:
                                case "sha256":
                                    input_data = {"message": test_case_text}
                                    # We warm first by running a single test case
                                    if start_option == "warm":
                                        executeTestCase(test_case_executable_dir, input_data)

                                    for i in range(iterations):
                                        test_case_result = executeTestCase(test_case_executable_dir, input_data)
                                        if(verifyTestCaseResponse(test_case_result["TestCaseResult"],operation)):
                                            print("succeed")
                                            reportToCloudWatch(test_case_id,log_group,log_stream_name,operation,arch_dir,test_case_result["ExecutionTime"],test_case_result["MaxMemoryUsed"],instance_type,index, i)
                                        else:
                                            print("ERROR IN TESTCASE:")
                                            print(test_case_result)

                            print("Test")
                        case "rust":
                            print("Test")
                        case "typescript":
                            print("Test")
                        case _:
                            return f"Unknown language: {language}"

if __name__ == "__main__":
    main()
