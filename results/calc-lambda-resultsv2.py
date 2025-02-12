import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
import itertools

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


# All in MB
memory_sizes = [
    128,
    512,
    1024,
    1769,
    3008
]

lambda_x86_pricing_per_ms = {
    128 : 0.0000000021,
    512 : 0.0000000083,
    1024 : 0.0000000167,
    1769: 0.0000000288,
    3008: 0.0000000490
}

lambda_arm_pricing_per_ms = {
    128 : 0.0000000017,
    512 : 0.0000000067,
    1024 : 0.0000000133,
    1769: 0.0000000230,
    3008: 0.0000000392
}

'''
lambda csv header
architecture,start_type,operation,language,memory_size,execution_time_ms,max_memory_usage_mb,init_duration_ms,billed_duration_ms
'''

# Define output directory for saved plots
output_dir_lambda = "assets/aws/lambda/"
os.makedirs(output_dir_lambda, exist_ok=True)
# Load CSV data
def load_data(file_path: str)->pd.DataFrame:
    """Load benchmark data from a CSV file."""
    return pd.read_csv(file_path)

def lighten_color(color, factor=0.6):
    """
    Lighten the color by a given factor.
    Factor should be between 0 and 1, where 1 means no change and 0 means full white.
    """
    color = color.lstrip('#')  # Remove the '#' at the start
    rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]  # Convert hex to RGB
    rgb = [int(c * factor) for c in rgb]  # Apply factor to lighten
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"  # Convert back to hex

# Define a function to filter middle 95% and compute mean
def middle_95_mean_execution_time_ms(group):
    lower = group['execution_time_ms'].quantile(0.025)  # 2.5th percentile
    upper = group['execution_time_ms'].quantile(0.975)  # 97.5th percentile
    filtered_group = group[(group['execution_time_ms'] >= lower) & (group['execution_time_ms'] <= upper)]
    return filtered_group['execution_time_ms'].mean()


def boxplot_per_operation_compare_x86_arm_start_type(df: pd.DataFrame):
    # get middle 95% mean
    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'memory_size', 'execution_time_ms']]
    
    # Compute the middle 95% mean execution time
    result = df_filtered.groupby(
        ['architecture', 'start_type', 'operation', 'language', 'memory_size']
    ).apply(middle_95_mean_execution_time_ms).reset_index(name='mean_execution_time_ms')

    # Pivot the data to get x86 and ARM side by side
    pivot_df = result.pivot_table(
        index=['start_type', 'operation', 'language', 'memory_size'], 
        columns='architecture', 
        values='mean_execution_time_ms'
    ).reset_index()


    print("")

# Function to create and save heatmaps
def heat_map_per_operation_compare_x86_arm_start_type(df: pd.DataFrame):

    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'memory_size', 'execution_time_ms']]
    
    # Compute the middle 95% mean execution time
    result = df_filtered.groupby(
        ['architecture', 'start_type', 'operation', 'language', 'memory_size']
    ).apply(middle_95_mean_execution_time_ms).reset_index(name='mean_execution_time_ms')

    # Pivot the data to get x86 and ARM side by side
    pivot_df = result.pivot_table(
        index=['start_type', 'operation', 'language', 'memory_size'], 
        columns='architecture', 
        values='mean_execution_time_ms'
    ).reset_index()

    # Ensure we only process rows that have both x86 and ARM data
    #pivot_df = pivot_df.dropna(subset=['x86', 'arm'])
    # EXAMPLE arm is 50 x86 is 100
    # (50 - 100 / 100) * 100 = -50% faster (50 percent faster but negative will mean arm)
    # EXAMPLE arm is 200 x86 is 20
    # (200-20 / 20) * 100 = 900% faster in x86

    pivot_df['percentage_difference'] = ((pivot_df['arm'] - pivot_df['x86']) / (pivot_df['x86'])) * 100
    # Compute percentage difference ((ARM - x86) / x86) * 100
    # Generate heatmaps per (start_type, operation)
    for (start_type, operation), group in pivot_df.groupby(['start_type', 'operation']):
        heatmap_data = group.pivot(index='memory_size', columns='language', values='percentage_difference')
        heatmap_data = heatmap_data.sort_index(ascending=False)  # Largest memory at the top
        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Arm Faster                                                      x86 Faster'}, center=0, linewidths=0.5)
        plt.title(f"% Change Performance (ARM vs x86) (95%) - {start_type}, {operation}")
        plt.xlabel("Programming Language", fontweight='bold')
        plt.ylabel("Memory Size (MB)",  fontweight='bold')

        # Save the figure instead of showing it
        filename = f"{output_dir_lambda}heatmap_per_operation_start_type/heatmap_{start_type}_{operation}.png"
        plt.savefig(filename, bbox_inches="tight")
        plt.close()  # Close the figure to free memory

    print(f"Heatmaps saved in '{output_dir_lambda}'")

def heat_map_per_operation_compare_cold_vs_warm(df:pd.DataFrame):

    print("")


def check_data(df:pd.DataFrame):
    # Create a DataFrame with all possible combinations
    expected_combinations = list(itertools.product(architectures, languages, operations, start_options, memory_sizes))
    expected_df = pd.DataFrame(expected_combinations, columns=['architecture', 'language', 'operation', 'start_option', 'memory_size'])

    # Assume `df` is your actual DataFrame to verify
    # (Replace `df` with your actual DataFrame variable)
    missing_combinations = expected_df.merge(df, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

    # Check if there are any missing combinations
    if missing_combinations.empty:
        print("✅ The DataFrame contains all expected combinations!")
    else:
        print("❌ Missing combinations found:")
        print(missing_combinations)


def analyze_lambda():
    aws_lambda_results_file_path = "cleaned-results-aws/Lambda-Results.csv"

    lambda_results_df = load_data(aws_lambda_results_file_path)
    heat_map_per_operation_compare_x86_arm_start_type(lambda_results_df)
    print("Finished Analyzing Lambdas.")

if __name__ == "__main__":
    print("Analyzing Lambda Results.")
    analyze_lambda()
