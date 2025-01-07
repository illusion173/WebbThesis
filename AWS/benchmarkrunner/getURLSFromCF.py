import boto3
import json

# Define the combinations for architectures and languages
architectures = ["x86", "arm"]
languages = ["c#", "go", "java", "python", "rust", "typescript"]

def get_cloudformation_outputs():

    # Initialize a CloudFormation client
    cf_client = boto3.client('cloudformation')

    # Get all stack summaries
    stacks = cf_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])['StackSummaries']

    aggregated_outputs = {}

    for stack in stacks:

        stack_name = stack['StackName']

        # Describe the stack to get detailed information
        stack_details = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]

        if 'Outputs' in stack_details:

            for output in stack_details['Outputs']:

                value = output['OutputValue']

                # (something like this: arm-python-rsa2048_decrypt-1769 : URL of lambda)
                print(value)
                try:
                    value_json = json.loads(value)
                    aggregated_outputs.update(value_json)
                except:
                    print("Unable to json serialize, moving on")

    return aggregated_outputs


if __name__ == "__main__":
    lambda_benchmark_urls = get_cloudformation_outputs()

    # Save the aggregated JSON to a file
    with open("lambda_benchmark_urls.json", "w") as json_file:
        json.dump(lambda_benchmark_urls, json_file, indent=4)

    #print("Aggregated outputs saved to aggregated_outputs.json")
