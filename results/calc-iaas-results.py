import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

architectures = [
    "x86",
    "arm"
]

languages = [
    'c#', # csharp is fully operational, for all combos.
    'go', # Go is fully operational, for all combos.
    'java', # Java is fully operational, for all combos.
    'python', # Python is fully operational, for all combos.
    'rust', # Rust is fully operational, for all combos
    'typescript', # Typescript is fully operational, for all combos.
]

languageKey = {
    'c#': '#5A2073',  # Teal for C#
    'go': '#00ADD8',   # Blue for Go
    'java': '#F80000', # Red for Java
    'python': '#FFD43B', # Yellow for Python
    'rust': '#D66B00', # Orange for Rust
    'typescript': '#3178C6', # Blue for TypeScript
}

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

start_options = [
    "cold",
    "warm"
]

# EC2 instance names for x86 architecture
ec2_x86_instances = [
    "t2.medium",
    "t2.xlarge",
    "t2.2xlarge"
]

# EC2 instance names for Arm architecture
ec2_arm_instances = [
    "t4g.medium",
    "t4g.xlarge",
    "t4g.2xlarge"
]
# Azure  virtual machine type names for x86 architecture
azure_x86_instances = [
    "B2s",
    "B4ms",
    "B8ms"
]

# Azure  virtual machine type names for x86 architecture
azure_arm_instances = [
    "B2pls_v2",
    "B4ps_v2",
    "B8ps_v2"
]

'''
ec2 csv header
id,instance_type,architecture,start_type,operation,language,iteration,execution_time_ms,avg_cpu_usage_percent,max_memory_usage_mb,avg_memory_usage_mb
'''

def load_csvs(file_names: list) -> pd.DataFrame:

    combined_df = pd.DataFrame()

    for file in file_names:
        if os.path.exists(file):
            df = pd.read_csv(file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"File not found: {file}")


    return combined_df

# Main execution
if __name__ == "__main__":
    print("Begin Analysis of IaaS")
    iaas_result_file_locs = ["./cleaned-results-aws/EC2-Results.csv", "./cleaned-results-azure/Azure-VM-Results.csv"]
    print("Loading of Iaas result csvs")
    iaas_df = load_csvs(iaas_result_file_locs)

    print("Finished Loading of result csvs")

    print("Finished Analyzing IaaS")

