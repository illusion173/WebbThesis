import boto3

EXCLUDE_FUNCTION_NAME = 'PythonTestLF'

# Create a Lambda client
lambda_client = boto3.client('lambda')

def delete_all_lambdas_except(exclude_function_name):
    # Get a list of all Lambda functions in your account
    paginator = lambda_client.get_paginator('list_functions')
    
    # Loop through the pages of Lambda functions
    for page in paginator.paginate():
        for function in page['Functions']:
            function_name = function['FunctionName']
            
            # Skip the function we want to exclude
            if function_name == exclude_function_name:
                print(f"Skipping Lambda function: {function_name} (excluded)")
                continue

            # Delete the Lambda function
            print(f"Deleting Lambda function: {function_name}")
            try:
                lambda_client.delete_function(FunctionName=function_name)
                print(f"Successfully deleted: {function_name}")
            except Exception as e:
                print(f"Error deleting {function_name}: {e}")

if __name__ == "__main__":
    delete_all_lambdas_except(EXCLUDE_FUNCTION_NAME)
