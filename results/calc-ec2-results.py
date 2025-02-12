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

languageColors = [
'#5A2073',
'#00ADD8'
'#F80000',
'#FFD43B',
'#D66B00',
'#3178C6'
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

start_options = [
    "cold",
    "warm"
]
# EC2 instance names for x86 architecture
x86_instances = [
    "t2.medium",
    "t2.xlarge",
    "t2.2xlarge"
]

# EC2 instance names for Arm architecture
arm_instances = [
    "t4g.medium",
    "t4g.xlarge",
    "t4g.2xlarge"
]

'''
ec2 csv header
id,instance_type,architecture,start_type,operation,language,iteration,execution_time_ms,avg_cpu_usage_percent,max_memory_usage_mb,avg_memory_usage_mb
'''
# Define output directory for saved plots
output_dir_ec2 = "assets/aws/ec2/"

os.makedirs(output_dir_ec2,exist_ok=True)

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



def ec2_gen_blox_plot(ec2_results_df: pd.DataFrame, operation: str, instance_type: str):
    """
    Create a box plot for execution times, grouped by architecture, instance_type, operation,
    and comparing cold start and warm start across all languages.
    """

    # Filter the dataframe for the given parameters
    filtered_df = ec2_results_df[
        (ec2_results_df['operation'] == operation) &
        (ec2_results_df['instance_type'] == instance_type)
    ]

    if filtered_df.empty:
        print(f"No data available for  operation={operation}, instance_type={instance_type}")
        return

    # Prepare the data for plotting
    data_by_language_and_start = {language: {'cold': [], 'warm': []} for language in languages}

    for language in languages:
        for start_option in start_options:
            # Collect execution times for each language and start_option
            execution_times = filtered_df[
                (filtered_df['language'] == language) & 
                (filtered_df['start_type'] == start_option)
            ]['execution_time_ms']

            # Filter to only the middle 95% (remove extreme outliers)
            if not execution_times.empty:
                lower_bound, upper_bound = np.percentile(execution_times, [2.5, 97.5])
                execution_times = execution_times[(execution_times >= lower_bound) & (execution_times <= upper_bound)]

           
            # Append the execution times to the respective start_option list
            data_by_language_and_start[language][start_option] = execution_times.tolist()

    # Create the box plot
    plt.figure(figsize=(18, 10))

    # Prepare positions for the box plots (add a bit more space between cold and warm)
    positions = np.arange(1, len(languages) * 2 + 1, 2)  # Space for both cold and warm start per language

    # Create box plots for each language, comparing cold and warm starts
    for idx, (language, start_data) in enumerate(data_by_language_and_start.items()):
        # Create a pair of positions for cold and warm starts for each language
        cold_data = start_data['cold']
        warm_data = start_data['warm']

        # Lighten the color for cold start
        cold_color = lighten_color(languageKey[language], factor=0.7)  # Lighten the color
        warm_color = languageKey[language]  # Use original color for warm start

        # Boxplot for cold start
        plt.boxplot(cold_data, positions=[positions[idx] - 0.3], widths=0.4, patch_artist=True,
                    boxprops=dict(facecolor=cold_color, color='black'),
                    medianprops=dict(color='yellow'),
                    whiskerprops=dict(color='black'),
                    capprops=dict(color='black'),
                    flierprops=dict(marker='o', color='red', alpha=0.5), showmeans=False)

        # Boxplot for warm start
        plt.boxplot(warm_data, positions=[positions[idx] + 0.3], widths=0.4, patch_artist=True,
                    boxprops=dict(facecolor=warm_color, color='black'),
                    medianprops=dict(color='yellow'),
                    whiskerprops=dict(color='black'),
                    capprops=dict(color='black'),
                    flierprops=dict(marker='o', color='red', alpha=0.5), showmeans=False)

    # Configure plot aesthetics
    plt.title(f"Execution Times - ( {instance_type} {operation}) 95%", fontsize=16)
    plt.xlabel("Languages", fontsize=14)
    plt.ylabel("Mean Execution Time (ms)", fontsize=14)
    plt.xticks(positions, languages, rotation=45, ha='right', fontsize=12)

    # Add a caption explaining the color scheme (darker is cold)
    plt.figtext(0.5, 0.025, "Darker colors represent cold start, lighter colors represent warm start", ha='center', va='bottom', fontsize=12, color='black')

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot
    filename = f"{output_dir_ec2}boxplot/{instance_type}_{operation}_cold_warm.png"
    plt.savefig(filename, bbox_inches='tight')

def ec2_gen_blox_plots(ec2_results_df: pd.DataFrame)->None:
    """
    Generate box plots for all combinations of instance_type, and operation.
    """
    for instance_type in x86_instances + arm_instances:  # Iterate over all instance types
        for operation in operations:
            ec2_gen_blox_plot(ec2_results_df, operation, instance_type)

def ec2_gen_bar_plot(ec2_results: pd.DataFrame, architecture: str, operation: str, instance_types: list) -> None:
    '''
    Create a bar plot for EC2 instances where the Y value is the execution time in ms.

    X will represent the EC2 instance types. Pair of bars for each language with darker color for cold start and lighter for warm start.
    Each bar will be colored according to the language key.
    '''
    # Filter the dataframe for the given parameters
    filtered_df = ec2_results[
        (ec2_results['architecture'] == architecture) &
        (ec2_results['operation'] == operation)
    ]

    if filtered_df.empty:
        print(f"No data available for architecture={architecture}, operation={operation}")
        return

    # Set up the plot file path
    filename = f"{output_dir_ec2}barplot/{architecture}_{operation}_cold_warm_ec2.png"

    # Begin plotting
    fig, ax = plt.subplots(figsize=(16, 10))

    bar_width = 0.15
    instance_spacing = 0.35  # Gap between EC2 instance types
    x_base = 0  # Starting x position
    x_ticks = []  # To set instance type positions
    x_tick_labels = []  # Instance type labels for the x-axis

    # Loop through all EC2 instance types (ensure these instance types correspond to the passed architecture)
    for i, instance_type in enumerate(instance_types):  # Use the passed instance types (x86 or ARM)
        # Ensure we are filtering based on the matching instance_type
        if architecture == "x86" and instance_type in x86_instances:
            x_pos = x_base  # Starting x position for this instance type group
        elif architecture == "arm" and instance_type in arm_instances:
            x_pos = x_base  # Starting x position for this instance type group
        else:
            continue  # Skip if instance type doesn't match architecture

        for language in languages:
            cold_filter = filtered_df[
                (filtered_df['instance_type'] == instance_type) & 
                (filtered_df['language'] == language) & 
                (filtered_df['start_type'] == 'cold') 
            ]

            cold_times = cold_filter['execution_time_ms']

            # Compute the 2.5th and 97.5th percentiles to remove extreme low and high values
            lower_bound, upper_bound = np.percentile(cold_times, [2.5, 97.5])

            # Keep only the values within this range (middle 95%)
            cold_time = cold_times[(cold_times >= lower_bound) & (cold_times <= upper_bound)]

            # Get the mean of the middle 95% of cold start cases
            cold_time_mean = cold_time.mean()

            warm_filter = filtered_df[
                (filtered_df['instance_type'] == instance_type) & 
                (filtered_df['language'] == language) & 
                (filtered_df['start_type'] == 'warm') 
            ]

            warm_times = warm_filter['execution_time_ms']

            # Compute the 2.5th and 97.5th percentiles to remove extreme low and high values
            lower_bound, upper_bound = np.percentile(warm_times, [2.5, 97.5])

            # Keep only the values within this range (middle 95%)
            warm_time = warm_times[(warm_times >= lower_bound) & (warm_times <= upper_bound)]

            # Get the mean of the middle 95% of warm start cases
            warm_time_mean = warm_time.mean()

            # Plot cold start bar
            if not pd.isna(cold_time_mean):
                ax.bar(x_pos, cold_time_mean, width=bar_width, color=lighten_color(languageKey[language]), label=f"{language} (cold)")
            
            # Plot warm start bar
            if not pd.isna(warm_time_mean):
                ax.bar(x_pos + bar_width, warm_time_mean, width=bar_width, color=languageKey[language], label=f"{language} (warm)")

            # Move x position for the next language pair
            x_pos += 2 * bar_width

        # Add instance type to x_ticks and leave space for the next instance type group
        x_ticks.append(x_base + bar_width * len(languages))
        x_tick_labels.append(instance_type)
        x_base = x_pos + instance_spacing

    # Configure the x-axis
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)
    ax.set_xlabel('EC2 Instance Type')
    ax.set_ylabel('Mean Execution Time (ms)')
    ax.set_title(f'Mean Execution Times ({architecture} - {operation}) 95%')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add a legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title="Language and Start Type", bbox_to_anchor=None, loc='upper right')

    # Save and show the plot
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def gen_bar_plots_for_ec2(ec2_results_df: pd.DataFrame) -> None:
    """
    Generate bar plots for both x86 and ARM EC2 instance types for each operation.
    """
    for architecture in architectures:
        for operation in operations:
            if architecture == "x86":
                # Generate plots for x86 EC2 instances only
                ec2_gen_bar_plot(ec2_results_df, architecture, operation, x86_instances)
            elif architecture == "arm":
                # Generate plots for ARM EC2 instances only
                ec2_gen_bar_plot(ec2_results_df, architecture, operation, arm_instances)



def gen_instance_type_comparison(ec2_results_df: pd.DataFrame):

    # Define EC2 instance types for x86 and arm architectures
    sizes = ["medium", "xlarge", "2xlarge"]
    x86_middle_95_means = []
    arm_middle_95_means = []
    percentage_diffs = []

    # For each instance type size (medium, xlarge, 2xlarge), calculate the mean of the middle 95% execution times
    for size in sizes:
        # Filter x86 data
        x86_data = ec2_results_df[(ec2_results_df['instance_type'].isin([f"t2.{size}", f"t2.{size}xlarge"])) & (ec2_results_df['architecture'] == 'x86')]
        arm_data = ec2_results_df[(ec2_results_df['instance_type'].isin([f"t4g.{size}", f"t4g.{size}xlarge"])) & (ec2_results_df['architecture'] == 'arm')]
        
        # Calculate the 2.5th and 97.5th percentiles for execution time for each operation
        if not x86_data.empty:
            x86_percentiles = x86_data.groupby('operation')['execution_time_ms'].quantile([0.025, 0.975]).unstack()
            # Filter the data to keep only the middle 95%
            x86_filtered = x86_data[
                x86_data.apply(
                    lambda row: x86_percentiles.loc[row['operation'], 0.025] <= row['execution_time_ms'] <= x86_percentiles.loc[row['operation'], 0.975],
                    axis=1
                )
            ]
            # Calculate the mean of the middle 95% for x86
            x86_middle_95_means.append(x86_filtered.groupby('operation')['execution_time_ms'].mean().mean())
        else:
            x86_middle_95_means.append(np.nan)

        if not arm_data.empty:
            arm_percentiles = arm_data.groupby('operation')['execution_time_ms'].quantile([0.025, 0.975]).unstack()
            # Filter the data to keep only the middle 95%
            arm_filtered = arm_data[
                arm_data.apply(
                    lambda row: arm_percentiles.loc[row['operation'], 0.025] <= row['execution_time_ms'] <= arm_percentiles.loc[row['operation'], 0.975],
                    axis=1
                )
            ]
            # Calculate the mean of the middle 95% for arm
            arm_middle_95_means.append(arm_filtered.groupby('operation')['execution_time_ms'].mean().mean())
        else:
            arm_middle_95_means.append(np.nan)

        # Calculate the percentage difference between x86 and Arm (if both values are available)
        if not np.isnan(x86_middle_95_means[-1]) and not np.isnan(arm_middle_95_means[-1]):
            diff = abs(x86_middle_95_means[-1] - arm_middle_95_means[-1]) / arm_middle_95_means[-1] * 100
            percentage_diffs.append(diff)
        else:
            percentage_diffs.append(np.nan)

    # Create a bar plot
    bar_width = 0.35
    index = np.arange(len(sizes))  # Positions for each group of bars

    fig, ax = plt.subplots(figsize=(8, 6))

    bar1 = ax.bar(index - bar_width/2, x86_middle_95_means, bar_width, label='t2.x86', color='blue')
    bar2 = ax.bar(index + bar_width/2, arm_middle_95_means, bar_width, label='t4g.Arm', color='orange')

    # Add labels, title, and legend
    ax.set_xlabel('Instance Size')
    ax.set_ylabel('Mean Execution Time (ms)')
    ax.set_title('Mean Middle 95% Execution Time for x86 vs Arm Instances')
    ax.set_xticks(index)
    ax.set_xticklabels(sizes)
    ax.legend()

    # Annotate percentage differences above bars
    for i in range(len(sizes)):
        if not np.isnan(percentage_diffs[i]):
            ax.text(i, max(x86_middle_95_means[i], arm_middle_95_means[i]) + 50, 
                    f'{percentage_diffs[i]:.2f}%', ha='center', color='black', fontsize=10)

    filename = f"{output_dir_ec2}arch_v_instance/mean_middle_95_execution_time_by_architecture_and_instance_type.png"
    # Save the figure to the specified path
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Plot saved to {filename}")
    plt.close()  # Close the plot to free up memory

def generate_arm_vs_x86_heatmaps(df):
    """
    This function generates heatmaps comparing ARM vs x86 architectures based on execution time
    for each programming language and EC2 instance size (medium, xlarge, 2xlarge) under both cold and warm start conditions.
    It computes the percentage difference, filters out the extreme values (top and bottom 2.5%) to keep the middle 95%,
    and creates heatmaps for both cold and warm starts.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the columns ['architecture', 'start_type', 'operation', 'language', 
                           'instance_type', 'execution_time_ms']
        output_dir_lambda (str): Path to the output directory where heatmaps will be saved.
    """
    output_dir = f"{output_dir_ec2}ec2_heatmaps"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Extract instance size (e.g., medium, xlarge, 2xlarge) from instance_type
    df['instance_size'] = df['instance_type'].str.extract(r'(medium|xlarge|2xlarge)', expand=False)

    # Filter relevant columns
    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'instance_size', 'execution_time_ms']]

    # Pivot to compare x86 and ARM times
    pivot_df = df_filtered.pivot_table(
        index=['start_type', 'language', 'instance_size'],
        columns='architecture',
        values='execution_time_ms'
    ).reset_index()


    # Check if the pivoted DataFrame has data
    if pivot_df.empty:
        print("Pivoted DataFrame is empty. No data available for comparison.")
        return

    # Compute percentage difference
    pivot_df['percentage_diff'] = ((pivot_df['x86'] - pivot_df['arm']) / pivot_df['arm']) * 100

    # Check if the 'percentage_diff' column has data
    if pivot_df['percentage_diff'].isnull().all():
        print("No valid data in 'percentage_diff' column. Check the input data for consistency.")
        return

    # Remove extreme cases (keep only the 95% most common cases)
    try:
        lower_bound, upper_bound = np.percentile(pivot_df['percentage_diff'], [2.5, 97.5])
        pivot_df = pivot_df[(pivot_df['percentage_diff'] >= lower_bound) & (pivot_df['percentage_diff'] <= upper_bound)]
    except ValueError:
        print("Error during percentile calculation. Likely due to insufficient data.")
        return

    # Check if the filtered DataFrame still contains data
    if pivot_df.empty:
        print("After filtering out extreme cases, the DataFrame is empty. No data to plot.")
        return

    # Save heatmaps for cold and warm starts
    for start in ["cold", "warm"]:
        plt.figure(figsize=(12, 8))

        # Filter by start type
        df_start = pivot_df[pivot_df['start_type'] == start]

        if start == "cold":
            print(df_start)

        # Pivot for heatmap (instance_size on Y-axis, language on X-axis)
        heatmap_data = df_start.pivot_table(index='instance_size', columns='language', values='percentage_diff')

        # Plot heatmap
        sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", center=0, fmt=".1f", vmin=-30, vmax=100)
        plt.title(f'ARM vs x86 Execution Time Difference (%) All Operations (95%) - {start.capitalize()} Start \n Negative Means x86 is Faster')
        plt.xlabel('Programming Language')
        plt.ylabel('Instance Size')

        # Save to disk
        filename = f"{output_dir}/execution_time_diff_{start}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

    print(f"Heatmaps saved in '{output_dir}' directory.")

def ec2_gen_architecture_cost_comparison(ec2_results_df: pd.DataFrame):
    print("")

def ec2_gen_architecture_cost_comparison_by_operation_and_language(ec2_results_df: pd.DataFrame):
    print("")

def generate_arm_vs_x86_heatmaps_for_operations(df):
    """
    This function generates heatmaps comparing ARM vs x86 architectures based on execution time
    for each programming language and EC2 instance size (medium, xlarge, 2xlarge) under both cold and warm start conditions.
    It computes the percentage difference, filters out the extreme values (top and bottom 2.5%) to keep the middle 95%,
    and creates heatmaps for both cold and warm starts, as well as for each operation.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the columns ['architecture', 'start_type', 'operation', 'language', 
                           'instance_type', 'execution_time_ms']
        output_dir_ec2 (str): Path to the output directory where heatmaps will be saved.
    """
    output_dir = f"{output_dir_ec2}ec2_heatmap_per_op"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Extract instance size (e.g., medium, xlarge, 2xlarge) from instance_type
    df['instance_size'] = df['instance_type'].str.extract(r'(medium|xlarge|2xlarge)', expand=False)

    # Filter relevant columns
    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'instance_size', 'execution_time_ms']]


    # Iterate through each operation and generate heatmap
    for operation in operations:
        # Filter DataFrame by operation
        df_operation = df_filtered[df_filtered['operation'] == operation]

        # Pivot to compare x86 and ARM times
        pivot_df = df_operation.pivot_table(
            index=['start_type', 'language', 'instance_size'],
            columns='architecture',
            values='execution_time_ms'
        ).reset_index()

        # Check if the pivoted DataFrame has data
        if pivot_df.empty:
            print(f"Pivoted DataFrame for {operation} is empty. No data available for comparison.")
            continue

        # Compute percentage difference
        pivot_df['percentage_diff'] = ((pivot_df['x86'] - pivot_df['arm']) / pivot_df['arm']) * 100

        # Check if the 'percentage_diff' column has data
        if pivot_df['percentage_diff'].isnull().all():
            print(f"No valid data in 'percentage_diff' column for {operation}. Check the input data for consistency.")
            continue

        # Remove extreme cases (keep only the 95% most common cases)
        try:
            lower_bound, upper_bound = np.percentile(pivot_df['percentage_diff'], [2.5, 97.5])
            pivot_df = pivot_df[(pivot_df['percentage_diff'] >= lower_bound) & (pivot_df['percentage_diff'] <= upper_bound)]
        except ValueError:
            print(f"Error during percentile calculation for {operation}. Likely due to insufficient data.")
            continue

        # Check if the filtered DataFrame still contains data
        if pivot_df.empty:
            print(f"After filtering out extreme cases, the DataFrame for {operation} is empty. No data to plot.")
            continue

        # Save heatmaps for cold and warm starts for each operation
        for start in ["cold", "warm"]:
            plt.figure(figsize=(12, 8))

            # Filter by start type
            df_start = pivot_df[pivot_df['start_type'] == start]

            # Pivot for heatmap (instance_size on Y-axis, language on X-axis)
            heatmap_data = df_start.pivot_table(index='instance_size', columns='language', values='percentage_diff')

            # Plot heatmap
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", center=0, fmt=".1f")
            plt.title(f'ARM vs x86 Execution Time Difference (%) - {operation} ({start.capitalize()} Start) \n Negative Means x86 is Faster')
            plt.xlabel('Programming Language')
            plt.ylabel('Instance Size')

            # Save to disk
            filename = f"{output_dir}/execution_time_diff_{operation}_{start}.png"
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()

        print(f"Heatmaps for {operation} saved in '{output_dir}' directory.")

def analyze_ec2():
    print("Running Analyzation For EC2")
    # Load the dataset
    aws_ec2_results_file_path = "cleaned-results-aws/EC2-Results.csv"

    ec2_r = load_data(aws_ec2_results_file_path)

    #ec2_gen_blox_plots(ec2_r)
    #gen_bar_plots_for_ec2(ec2_r)
    #gen_instance_type_comparison(ec2_r)
    #generate_arm_vs_x86_heatmaps_for_operations(ec2_r)
    generate_arm_vs_x86_heatmaps(ec2_r)

# Main execution
if __name__ == "__main__":
    print("Analyzing EC2")
    # Function to facilitate EC2 analyzation
    analyze_ec2()
    


