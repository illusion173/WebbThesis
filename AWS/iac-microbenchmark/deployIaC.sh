#!/bin/bash

# For some reason timeouts are an issue while deploying, this will automate per stack, similar to --all
#
# List of stack names
stacks=(
    #"IaCBenchMark-Build-Lambdas-csharp-x86"
    "IaCBenchMark-Build-Lambdas-go-x86"
   # "IaCBenchMark-Build-Lambdas-java-x86" deployed
    #"IaCBenchMark-Build-Lambdas-python-x86" # deployed
    #"IaCBenchMark-Build-Lambdas-rust-x86" # deployed
    #"IaCBenchMark-Build-Lambdas-typescript-x86" # deployed
    #"IaCBenchMark-Build-Lambdas-csharp-arm"
    "IaCBenchMark-Build-Lambdas-go-arm"
   # "IaCBenchMark-Build-Lambdas-java-arm" # deployed
    #"IaCBenchMark-Build-Lambdas-python-arm" # deployed
    #"IaCBenchMark-Build-Lambdas-rust-arm" # deployed
    #"IaCBenchMark-Build-Lambdas-typescript-arm" # deployed
)

# Loop through each stack
for stack in "${stacks[@]}"
do
    echo "Deploying $stack..."
    cdk deploy --require-approval never "$stack"

    # Check if the command succeeded
    if [ $? -ne 0 ]; then
        echo "Deployment failed for $stack. Exiting."
        exit 1
    fi

    # Sleep for 1 minute
    echo "Sleeping for 1 minute before deploying the next stack..."
    sleep 60
done

echo "All stacks deployed successfully!"
