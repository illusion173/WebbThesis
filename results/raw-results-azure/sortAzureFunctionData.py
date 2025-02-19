import pandas as pd
from datetime import datetime
import json
import pytz
def load_benchmark_data(json_file):
    """Load and parse benchmark JSON file"""
    benchmark_windows = []
    with open(json_file, 'r') as f:
        data = json.load(f)
        for entry in data:
            benchmark_windows.append({
                'operation_name': entry['operationName'],
                'start_time': entry['benchmarktimes'][0],
                'end_time': entry['benchmarktimes'][1],
                'start_type': entry['start_type']
            })
    return benchmark_windows


def load_csv_data(csv_file_name):

    df = pd.read_csv(csv_file_name, encoding='utf-7')

    cleaned_df = df[['timestamp', 'name', 'customDimensions']]

    cleaned_df['timestamp'] = cleaned_df['timestamp'].apply(format_timestamp)

    cleaned_df['name'] = cleaned_df['name'].apply(format_op_names)

    return cleaned_df

def split_operation_name(s):
    # First get the language by splitting on first underscore
    language = s.split('_', 1)[0]

    if language == "dotnet":
        language = "c#"
    # Then get everything between the first underscore and '_program' if it exists
    operation = s.split('_', 1)[1]
    if '_program' in operation:
        operation = operation.replace('_program', '')
        
    return language, operation

def format_timestamp(original_time):

    # Parse the timestamp assuming it is already in UTC
    dt = datetime.strptime(original_time, "%m/%d/%Y, %I:%M:%S.%f %p")

    # Format to ISO 8601 (UTC)
    formatted_time = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    dt_object = datetime.strptime(formatted_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt_object 


def format_op_names(s):
    # First get the language by splitting on first underscore
    language = s.split('_', 1)[0]

    if language == "dotnet":
        language = "c#"
    
    # Then get everything between the first underscore and '_program' if it exists
    operation = s.split('_', 1)[1]
    if '_program' in operation:
        operation = operation.replace('_program', '')

    cleaned_op = f"{language}_{operation}"
        
    return cleaned_op

def get_benchmark_rows(bench_data_json, data_csv):
    data_rows = []

    for row in bench_data_json:
        operationname = row['operation_name']

        start_time = row['start_time']
        end_time = row['end_time']

        # Convert benchmark times to datetime objects for comparison
        start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
        end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
        
        # Grab the values between start and end time, match the operation name.
        # Filter the DataFrame
        filtered_rows = data_csv[
            (data_csv['timestamp'] >= start_time_dt) &
            (data_csv['timestamp'] <= end_time_dt) &
            (data_csv['name'] == operationname)
        ]

        for index, filtered_row in filtered_rows.iterrows():
            # Grab the json from the customDimensions
            customDimensionStr = filtered_row['customDimensions']
            customDimensionJson = json.loads(customDimensionStr)
            
            new_data_row = {}

            start_type = row['start_type']

            language, operation = split_operation_name(operationname)

            new_data_row['start_type'] = start_type
            new_data_row['language'] = language
            new_data_row['architecture'] = 'x86'
            new_data_row['operation'] = operation
            new_data_row['execution_time_ms'] = customDimensionJson['FunctionExecutionTimeMs']


            data_rows.append(new_data_row)

    return data_rows


if __name__ == "__main__":
    data_file = "azurefunctionx86Data.csv"
    warm_times = "warm-azurefunc-BenchmarkTimes.json"
    cold_times = "cold-azurefunc-BenchmarkTimes.json"

    # Define CSV file path
    output_csv_file = 'azurefunc-benchmarktimes.csv'


    csv_data_df = load_csv_data(data_file)

    cold_benchmark_data = load_benchmark_data(cold_times)

    cold_rows = get_benchmark_rows(cold_benchmark_data, csv_data_df)
    warm_benchmark_data = load_benchmark_data(warm_times)

    warm_rows = get_benchmark_rows(warm_benchmark_data, csv_data_df)
    final_data_rows = cold_rows + warm_rows
    print(final_data_rows)
    # Convert list of dictionaries to a DataFrame
    df = pd.DataFrame(final_data_rows)
    # Write the DataFrame to a CSV file
    df.to_csv(output_csv_file, index=False)

    print(f"Data written to {output_csv_file}")


    
