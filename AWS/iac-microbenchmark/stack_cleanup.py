
import boto3
import time

# Create a CloudFormation client
cf_client = boto3.client('cloudformation')

def delete_all_stacks():
    # Get a list of all CloudFormation stacks in your account
    paginator = cf_client.get_paginator('describe_stacks')
    
    # Loop through the pages of CloudFormation stacks
    for page in paginator.paginate():
        for stack in page['Stacks']:
            stack_name = stack['StackName']
            
            # Skip deletion of stacks in DELETE_COMPLETE state (already deleted)
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                print(f"Stack {stack_name} is already deleted, skipping.")
                continue

            # Deleting the CloudFormation stack
            print(f"Deleting CloudFormation stack: {stack_name}")
            try:
                cf_client.delete_stack(StackName=stack_name)
                print(f"Successfully initiated deletion for: {stack_name}")
                # Wait until the stack deletion completes
                wait_for_stack_deletion(stack_name)
            except Exception as e:
                print(f"Error deleting {stack_name}: {e}")

def wait_for_stack_deletion(stack_name):
    """Wait for the CloudFormation stack deletion to complete."""
    print(f"Waiting for stack {stack_name} to be deleted...")
    while True:
        try:
            cf_client.describe_stacks(StackName=stack_name)
            time.sleep(60)
        except cf_client.exceptions.ClientError as e:
            if 'StackNotFound' in str(e):
                print(f"Stack {stack_name} deleted successfully.")
                break
            else:
                print(f"Error checking stack status: {e}")
                break

if __name__ == "__main__":
    delete_all_stacks()
