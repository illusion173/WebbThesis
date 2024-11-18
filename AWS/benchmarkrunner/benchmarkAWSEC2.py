import time
import json
import requests
import platform
import subprocess
import psutil
import uuid
import pandas as pd
import os

def calculate_average_cpu_usage(cpus_before, cpus_after):
    total_idle_diff = 0
    total_time_diff = 0

    # Calculate the total idle and total time differences for all cores
    for t0, t1 in zip(cpus_before, cpus_after):
        # Calculate the difference in idle time
        idle_diff = t1.idle - t0.idle

        # Calculate the difference in total time
        total_diff = (
            (t1.user - t0.user) +
            (t1.nice - t0.nice) +
            (t1.system - t0.system) +
            (t1.idle - t0.idle) +
            (t1.iowait - t0.iowait) +
            (t1.irq - t0.irq) +
            (t1.softirq - t0.softirq) +
            (t1.steal - t0.steal)
        )

        total_idle_diff += idle_diff
        total_time_diff += total_diff

    # Calculate the average CPU usage
    if total_time_diff > 0:
        average_usage = 100.0 * (1.0 - (total_idle_diff / total_time_diff))
    else:
        average_usage = 0.0

    return round(average_usage, 2)

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
        try:
            # Open and load the JSON content
            with open(input_data_loc, 'r') as file:
                test_case_inputs[operation] = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found - {input_data_loc}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {input_data_loc}: {e}")

    return test_case_inputs

def save_testcase_results(finished_test_cases: list, file_name: str) -> None:
    """
    Save the test case results to a CSV file using pandas.
    """
    # List to hold all rows of data
    data_rows = []

    # Format the data for saving
    for finished_test_case in finished_test_cases:

        test_case_results, test_case = finished_test_case
        
        # Extract relevant data from each test case and result iteration
        for test_case_result in test_case_results:

            data_row = {
                "id": test_case.get("id", ""),
                "instance_type": test_case.get("instance_type", ""),
                "architecture": test_case.get("architecture", ""),
                "start_type": test_case.get("start_type", ""),
                "operation": test_case.get("operation", ""),
                "language": test_case.get("language", ""),
                "iteration": test_case_result.get("iteration", 0),
                "execution_time_ms": test_case_result.get("execution_time", 0),
                "avg_cpu_usage_percent": test_case_result.get("avg_cpu_usage", 0),
                "max_memory_usage_mb": test_case_result.get("max_memory_usage", 0),
                "avg_memory_usage_mb": test_case_result.get("avg_memory_usage", 0),
            }

            data_rows.append(data_row)

    # Convert list of dictionaries to a DataFrame
    df = pd.DataFrame(data_rows)
    
    # Save DataFrame to a CSV file
    try:
        df.to_csv(file_name, index=False)
        print(f"Results successfully saved to {file_name}")
    except Exception as e:
        print(f"Failed to save results: {e}")

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
            print(f"Unable to retrieve instance type. Status code: {response.status_code}")
            exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error querying instance metadata: {e}")
        exit(1)


def to_pascal_case(snake_str):
    # Convert snake_case to PascalCase
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def convert_dict_keys(input_dict):
    # Create a new dictionary with transformed keys
    return {to_pascal_case(key): value for key, value in input_dict.items()}

def create_tc(arch_dir: str, language: str, operation: str, input: dict, correct_answer: dict, start_type: str, instance_type: str, iterations: int)-> dict:
    # Get the base directory where the script is being executed
    base_dir = str(os.path.dirname(os.path.abspath(__file__)))
    new_file_base_str = f"iac-microbenchmark/ec2/{language}/{arch_dir}/{operation}"
    file_executable_location = base_dir.replace("benchmarkrunner", new_file_base_str)

    # Mapping of language to command and file location format
    language_settings = {
        'c#': {"command": "", "file_loc": f"{file_executable_location}"},
        'go': {"command": "", "file_loc": f"{file_executable_location}"},
        'java': {"command": "java -jar", "file_loc": f"{file_executable_location}-1.0-SNAPSHOT.jar"},
        'python': {"command": "python3.11", "file_loc": f"{file_executable_location}.py"},
        'rust': {"command": "", "file_loc": f"{file_executable_location}"},
        'typescript': {"command": "node", "file_loc": f"{file_executable_location}.js"}
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

    # Need to fix this later, this is to fix serialization issues
    if language == "c#":
        input = convert_dict_keys(input)


    # Build the test case
    test_case = {
        "id" : str(uuid.uuid4()), # generate a unique id for the test case
        "command": settings["command"],
        "file_loc": settings["file_loc"],
        "operation_input": input,
        "validation": correct_answer,
        "start_type": start_type,
        "iterations": iterations,
        "operation" : operation,
        "language" : language,
        "architecture" : arch_dir,
        "instance_type": instance_type
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
            stderr=subprocess.PIPE,
            shell=False
        )
        
        while process.poll() is None:  # While the script is still running
            # Update peak memory and CPU usage
            time.sleep(0.01)

        return
    except Exception as e:
        print(f"Error occurred in warmup: {e}")
        raise e
    

def execute_tc(test_case: dict) -> list:
    subprocess_input = []
    test_case_results = []

    # So input can be command, file loc, input
    # or for executables file_loc, input
    # This means that it is an executable
    if test_case["command"] == "":
        subprocess_input.append(test_case["file_loc"])
    else:
        # Python, JavaScript, Java
        subprocess_input.extend(test_case["command"].split())

        subprocess_input.append(test_case["file_loc"])

    # Always add input to the end as an argument
    op_input = test_case["operation_input"]


    subprocess_input.append(json.dumps(op_input))


    # Retrieve how many times we need to run this test case
    num_iterations = test_case["iterations"]

    # Check if we need to do a warm-up, execute the operations 50 times to warm up
    if test_case["start_type"] == "warm":
        print("Begin Warmup")
        for i in range(0, 10):
            execute_warmup(subprocess_input)
        print("Finished Warmup")
    else:
        print("No Warmup")

    for iteration in range(num_iterations):
        print(f"Test Case Iteration: {iteration}")
        start_time = 0.0
        end_time = 0.0
        mem_usage_samples = []  # to store memory usage samples

        # Final result dict
        singular_test_case_result = {}

        # Start the timer
        start_time = time.perf_counter()

        # record times before execution 
        cpus_before = psutil.cpu_times(percpu=True)

        # Use subprocess to run the operation
        process = subprocess.Popen(
            subprocess_input,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )

        # Create a process object for tracking memory
        process_psutil = psutil.Process(process.pid)

        try:
            # Monitor the process while it's running
            while True:  # While the script is still running
                if process_psutil.is_running() and not process_psutil.status() == psutil.STATUS_ZOMBIE:
                    
                    # Update memory samples
                    mem_usage_samples.append(process_psutil.memory_info().rss)
                else:
                    # After process finishes, record the end time of execution
                    end_time = time.perf_counter()
                    break
        except Exception as e:
            process.kill()  # Ensure the process is killed in case of any exception
            print(f"Error occurred: {e}")
            exit(1)

        # Capture the second snapshot of CPU times
        cpus_after = psutil.cpu_times(percpu=True)

        average_cpu_usage = calculate_average_cpu_usage(cpus_before, cpus_after)

        execution_time = end_time - start_time

        # Calculate average and max memory usage
        average_mem_usage = sum(mem_usage_samples) / len(mem_usage_samples) if mem_usage_samples else 0

        max_mem = max(mem_usage_samples)

        # Retrieve the process output
        stdout, stderr = process.communicate()

        if stderr.decode() != "":
            print(type(stderr))
            print(f"stderr: {stderr.decode()}")

        # Grab the function's output for verification
        try:
            test_case_output = json.loads(stdout.decode())
            print("TESTCASE OUTPUT:")
            print(test_case_output)
            print("")
        except json.JSONDecodeError:
            print("Failed to decode JSON from stdout")
            print(f"Original: {stdout.decode()}")
            test_case_output = {}

        # Compile results into dict
        singular_test_case_result["execution_time"] = execution_time * 1000  # Convert to ms
        singular_test_case_result["avg_cpu_usage"] = average_cpu_usage  # in % float
        singular_test_case_result["max_memory_usage"] = max_mem / (1024 ** 2)  # Convert to MB
        singular_test_case_result["avg_memory_usage"] = average_mem_usage / (1024 ** 2)  # Convert to MB
        singular_test_case_result["iteration"] = iteration  # int
        singular_test_case_result["test_case_id"] = test_case["id"]

        test_case_results.append(singular_test_case_result)

    return test_case_results

def main():

    # Get Architecture
    architecture = platform.machine()

    #instance_type = get_instance_type()
    instance_type = "TEST"

    if architecture == "x86_64":
        arch_dir = "x86"
    else:
        arch_dir = "arm"

    # use comments to select specific test cases

    languages = [
        #'c#',
        #'go',
        #'java',
        'python',
        #'rust',
        #'typescript',
    ]

    operations = [
        #'aes256_decrypt', # works for all
        #'aes256_encrypt', # works for all
        'ecc256_sign',
        #'ecc256_verify',
        'ecc384_sign',
        #'ecc384_verify',
        #'rsa2048_decrypt',
        #'rsa2048_encrypt',
        #'rsa3072_decrypt',
        #'rsa3072_encrypt',
        #'rsa4096_decrypt',
        #'rsa4096_encrypt',
        #'sha256', # works for all
        #'sha384', # works for all
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
    iterations = 3

    # To save the results
    save_result_file_name = f"./{architecture}-{instance_type}-AWSEC2-Benchmarkresults.csv"

    finished_test_cases = []

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

    print("")
    print("")

    print("Beginning AWS EC2 Benchmark Runnner")
    print(f"Architecture: {architecture}")
    print(f"Instance Type: {instance_type}")


    for test_case in test_cases:
        test_case_operation = test_case["operation"]
        test_case_language = test_case["language"]
        test_case_start_type = test_case["start_type"]
        print("---------------------------------------")
        print(f"Executing Test Case")
        print(f">Operation: {test_case_operation}")
        print(f">Language: {test_case_language}")
        print(f">Start Type: {test_case_start_type}")

        # Execute Test Case
        test_case_result = execute_tc(test_case)

        # Save a tuple containing the results and the test case into a list to save for later
        finished_test_cases.append((test_case_result,test_case))
        print("Finished Test Case.")
        print("---------------------------------------")
        print("")
        # Sleep for a second before moving on to next test case to settle
        time.sleep(0.05)

    print("Finished AWS EC2 Benchmark Runner")

    save_testcase_results(finished_test_cases, save_result_file_name)
    
    print(f"Saved Results to file: {save_result_file_name}")

    exit(0)

if __name__ == "__main__":
    print("Begin Initialization of AWS EC2 Benchmark runner")
    main()
