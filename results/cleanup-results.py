import pandas as pd
import os

# File lists
lambda_files = [
    "Lambda-Benchmark-Results-cold-rust-python-typescript.csv",
    "Lambda-Benchmark-Results-warm-rust-python-typescript.csv",
    "Lambda-Benchmark-Results-cold-java-csharp-go.csv",
    "Lambda-Benchmark-Results-warm-java-csharp-go.csv"
]

ec2_files = [
    "aarch64-t4g.2xlarge-AWSEC2-Benchmarkresults.csv",
    "aarch64-t4g.xlarge-AWSEC2-Benchmarkresults.csv",
    "x86_64-t2.medium-AWSEC2-Benchmarkresults.csv",
    "aarch64-t4g.medium-AWSEC2-Benchmarkresults.csv",
    "x86_64-t2.2xlarge-AWSEC2-Benchmarkresults.csv",
    "x86_64-t2.xlarge-AWSEC2-Benchmarkresults.csv"
]




azure_vm_files = [
"aarch64-standard_b2pls_v2-AzureVM-Benchmarkresults.csv",
"aarch64-standard_b4ps_v2-AzureVM-Benchmarkresults.csv",   
"aarch64-standard_b8ps_v2-AzureVM-Benchmarkresults.csv",
"x86_64-standard_b2s-AzureVM-Benchmarkresults.csv",
"x86_64-standard_b4ms-AzureVM-Benchmarkresults.csv"
"x86_64-standard_b8ms-AzureVM-Benchmarkresults.csv"
]

# Combine CSV files into one dataframe
def combine_csv(files, output_file):
    """Combine multiple CSV files into one and save to output_file."""
    combined_df = pd.DataFrame()

    for file in files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"File not found: {file}")

    combined_df.to_csv(output_file, index=False)
    print(f"Combined file saved to {output_file}")



def azure_clean_cols(file_name):

    cleaned_df = pd.DataFrame()

    df = pd.read_csv(file_name)
    cleaned_df = pd.concat([cleaned_df, df], ignore_index=True)

    cleaned_df["instance_type"] = df["instance_type"].str.replace("standard_", "", regex=True)

    cleaned_df.to_csv("clean-azure-vm.csv", index=False)


# Main script
if __name__ == "__main__":
    # Combine Lambda results
    #combine_csv(lambda_files, "Lambda-Results.csv")

    # Combine EC2 results
    #combine_csv(ec2_files, "EC2-Results.csv")
    
    # Combine Azure VM results into single file.

    combine_csv(azure_vm_files, "Azure-VM-Results.csv")
