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

def save_architecture_comparison_heatmaps(df):
    output_dir = f"{output_dir_lambda}heatmaps"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Filter relevant columns
    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'memory_size', 'execution_time_ms']]
    
    # Pivot to compare x86 and ARM times
    pivot_df = df_filtered.pivot_table(
        index=['start_type', 'operation', 'language', 'memory_size'],
        columns='architecture',
        values='execution_time_ms'
    ).reset_index()

    # Compute percentage difference
    pivot_df['percentage_diff'] = ((pivot_df['x86'] - pivot_df['arm']) / pivot_df['arm']) * 100

    # Remove extreme cases (keep only the 95% most common cases)
    lower_bound, upper_bound = np.percentile(pivot_df['percentage_diff'], [2.5, 97.5])
    pivot_df = pivot_df[(pivot_df['percentage_diff'] >= lower_bound) & (pivot_df['percentage_diff'] <= upper_bound)]

    # Save heatmaps for cold and warm starts
    for start in ["cold", "warm"]:
        plt.figure(figsize=(12, 8))
        
        # Filter by start type
        df_start = pivot_df[pivot_df['start_type'] == start]
        
        # Pivot for heatmap
        heatmap_data = df_start.pivot_table(index='memory_size', columns='language', values='percentage_diff')

        # Plot heatmap
        sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", center=0, fmt=".1f")
        plt.title(f'ARM vs x86 Execution Time Difference (%) All Operations (95%) - {start.capitalize()} Start \n Negative Means x86 is Faster')
        plt.xlabel('Programming Language')
        plt.ylabel('Memory Size (MB)')

        # Save to disk
        filename = f"{output_dir}/execution_time_diff_{start}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

    print(f"Heatmaps saved in '{output_dir}' directory.")

def save_operation_specific_heatmaps(df):
    output_dir = f"{output_dir_lambda}heatmap_per_op"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Filter relevant columns
    df_filtered = df[['architecture', 'start_type', 'operation', 'language', 'memory_size', 'execution_time_ms']]
    
    # Pivot to compare x86 and ARM times
    pivot_df = df_filtered.pivot_table(
        index=['start_type', 'operation', 'language', 'memory_size'],
        columns='architecture',
        values='execution_time_ms'
    ).reset_index()

    # Compute percentage difference
    pivot_df['percentage_diff'] = ((pivot_df['x86'] - pivot_df['arm']) / pivot_df['arm']) * 100

    # Remove extreme cases (keep only the 95% most common cases)
    lower_bound, upper_bound = np.percentile(pivot_df['percentage_diff'], [2.5, 97.5])
    pivot_df = pivot_df[(pivot_df['percentage_diff'] >= lower_bound) & (pivot_df['percentage_diff'] <= upper_bound)]

    # Generate heatmaps for each operation and start type
    for operation in pivot_df['operation'].unique():
        for start in ["cold", "warm"]:
            plt.figure(figsize=(12, 8))

           

            # Filter data for operation and start type
            df_op = pivot_df[(pivot_df['operation'] == operation) & (pivot_df['start_type'] == start)]

            if operation == "sha384":
                print(df_op)
            
            # Pivot for heatmap
            heatmap_data = df_op.pivot_table(index='memory_size', columns='language', values='percentage_diff')

            # Plot heatmap
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", center=0, fmt=".1f")
            plt.title(f'ARM vs x86 Execution Time Diff (%) - {operation} - {start.capitalize()} Start \n Negative Means x86 is Faster')
            plt.xlabel('Programming Language')
            plt.ylabel('Memory Size (MB)')

            # Save to disk
            filename = f"{output_dir}/execution_time_diff_{operation}_{start}.png"
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()

    print(f"Heatmaps saved in '{output_dir}' directory.")


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

def gen_blox_plot(lambda_results_df: pd.DataFrame, architecture: str, operation: str, memory_size: int):
    """
    Create a box plot for execution times, grouped by architecture, memory size, operation,
    and comparing cold start and warm start across all languages.
    """

    # Filter the dataframe for the given parameters
    filtered_df = lambda_results_df[
        (lambda_results_df['architecture'] == architecture) &
        (lambda_results_df['operation'] == operation) &
        (lambda_results_df['memory_size'] == memory_size)
    ]

    if filtered_df.empty:
        print(f"No data available for architecture={architecture}, operation={operation}, memory_size={memory_size}")
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

            # Filter to only the top 95% (remove extreme outliers)
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
    plt.title(f"Execution Times - ({architecture} {memory_size}MB {operation}) 95%", fontsize=16)
    plt.xlabel("Languages", fontsize=14)
    plt.ylabel("Mean Execution Time (ms)", fontsize=14)
    plt.xticks(positions, languages, rotation=45, ha='right', fontsize=12)

    # Add a caption explaining the color scheme (darker is cold)
    plt.figtext(0.5, 0.025, "Darker colors represent cold start, lighter colors represent warm start", ha='center', va='bottom', fontsize=12, color='black')

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot
    filename = f"{output_dir_lambda}boxplot/{architecture}_{memory_size}MB_{operation}_cold_warm.png"
    plt.savefig(filename, bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    #print(f"Saved box plot (Cold/Warm Comparison with Spacing): {filename}")

def gen_blox_plots(lambda_results_df: pd.DataFrame)->None:

    for architecture in architectures:
        for memory_size in memory_sizes:
            for operation in operations:
                gen_blox_plot(lambda_results_df, architecture,operation, memory_size)
    

def gen_bar_plot(lambda_results_df: pd.DataFrame, architecture: str, operation: str)->None:
    '''
    Create a bar plot where the Y value is the execution time in ms.

    X should be memory size. Pair of bar plot for each language darker color representing the cold start, lighter color representing the warm start.
    Each bar should be a color relating to language key.
    '''
    # Filter the dataframe for the given parameters
    filtered_df = lambda_results_df[
        (lambda_results_df['architecture'] == architecture) &
        (lambda_results_df['operation'] == operation) 
    ]

    if filtered_df.empty:
        print(f"No data available for architecture={architecture}, operation={operation}")
        return

    # Set up the plot file path
    filename = f"{output_dir_lambda}barplot/{architecture}_{operation}_cold_warm.png"

    # Begin plotting
    fig, ax = plt.subplots(figsize=(16, 10))
    
    bar_width = 0.15
    memory_spacing = 0.35  # Gap between memory size groups
    x_base = 0  # Starting x position
    x_ticks = []  # To set memory size positions
    x_tick_labels = []  # Memory size labels for the x-axis

    for i, memory_size in enumerate(memory_sizes):
        x_pos = x_base  # Starting x position for this memory size group
        for language in languages:

            cold_times = filtered_df[
                (filtered_df['memory_size'] == memory_size) &
                (filtered_df['language'] == language) &
                (filtered_df['start_type'] == 'cold')
            ]['execution_time_ms']

            # Compute the 2.5th and 97.5th percentiles to remove extreme low and high values
            lower_bound, upper_bound = np.percentile(cold_times, [2.5, 97.5])

            # Keep only the values within this range (middle 95%)
            cold_time = cold_times[(cold_times >= lower_bound) & (cold_times <= upper_bound)]

            # Get the mean of the middle 95% of cold start cases
            cold_time_mean = cold_time.mean()


            warm_times = filtered_df[
                (filtered_df['memory_size'] == memory_size) &
                (filtered_df['language'] == language) &
                (filtered_df['start_type'] == 'warm')
            ]['execution_time_ms']
            

            # Compute the 2.5th and 97.5th percentiles to remove extreme low and high values
            lower_bound, upper_bound = np.percentile(warm_times, [2.5, 97.5])

            # Keep only the values within this range (middle 95%)
            warm_time = warm_times[(warm_times >= lower_bound) & (warm_times <= upper_bound)]

            # Get the mean of the middle 95% of warm start cases
            warm_time_mean = warm_time.mean()

            # Plot cold start
            if not pd.isna(cold_time_mean):
                ax.bar(x_pos, cold_time, width=bar_width, color=lighten_color(languageKey[language]), label=f"{language} (cold)")
            
            # Plot warm start
            if not pd.isna(warm_time_mean):
                ax.bar(x_pos + bar_width, warm_time, width=bar_width, color=languageKey[language], label=f"{language} (warm)")

            # Move x position for the next language pair
            x_pos += 2 * bar_width

        # Add memory size to x_ticks and leave space for the next memory size group
        x_ticks.append(x_base + bar_width * len(languages))
        x_tick_labels.append(str(memory_size))
        x_base = x_pos + memory_spacing

    # Configure the x-axis
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)
    ax.set_xlabel('Memory Size (MB)')
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

def gen_bar_plots(lambda_results_df: pd.DataFrame)->None:

    for architecture in architectures:
        for operation in operations:
            gen_bar_plot(lambda_results_df, architecture, operation )


def gen_architecture_comparison(lambda_results_df: pd.DataFrame):
    # Step 1: Calculate the 2.5th and 97.5th percentiles for execution time based on architecture and memory size
    percentiles = lambda_results_df.groupby(['architecture', 'memory_size'])['execution_time_ms'].quantile([0.025, 0.975]).unstack()

    # Step 2: Filter the data to keep only the middle 95% (between 2.5th and 97.5th percentiles)
    filtered_data = lambda_results_df[
        lambda_results_df.apply(
            lambda row: percentiles.loc[row['architecture'], row['memory_size']][0.025] <= row['execution_time_ms'] <= percentiles.loc[row['architecture'], row['memory_size']][0.975],
            axis=1
        )
    ]

    # Step 3: Group by architecture and memory size, then calculate the mean of the middle 95%
    mean_execution_by_memory = (
        filtered_data.groupby(['architecture', 'memory_size'])['execution_time_ms']
        .mean()
        .reset_index()
    )

    # Step 4: Pivot the table for easier percentage difference calculation
    pivot = mean_execution_by_memory.pivot(index='memory_size', columns='architecture', values='execution_time_ms').reset_index()
    # Calculate percentage difference (arm vs x86)
    pivot['percentage_difference'] = ((pivot['x86'] - pivot['arm']) / pivot['arm']) * 100 * -1 # make it positive

    # Get unique architectures and memory sizes
    architectures = ['arm', 'x86']  # Swapped order
    memory_sizes = pivot['memory_size']

    # Prepare the data for plotting
    x = range(len(memory_sizes))  # X-axis positions for memory sizes
    width = 0.4  # Width of the bars

    # Plot
    plt.figure(figsize=(12, 6))

    # Plot bars for arm and x86 (swapped order)
    plt.bar(
        [pos - width / 2 for pos in x],  # Position bars for arm
        pivot['arm'], 
        width, 
        label='arm', 
        color='orange'
    )
    plt.bar(
        [pos + width / 2 for pos in x],  # Position bars for x86
        pivot['x86'], 
        width, 
        label='x86', 
        color='blue'
    )

    # Add percentage difference as text above each pair of bars
    for i, row in pivot.iterrows():
        percentage = row['percentage_difference']
        # Position text above the taller bar
        y_pos = max(row['x86'], row['arm']) + 2
        plt.text(i, y_pos, f"{percentage:.1f}%", ha='center', color='black', fontsize=10)

    # Add labels and titles
    plt.title("Mean Execution Time All Operations by Architecture and Memory Size (95%)")
    plt.xlabel("Memory Size (MB)")
    plt.ylabel("Mean Execution Time (ms)")

    # Format x-axis
    plt.xticks([pos for pos in x], memory_sizes)  # Center ticks
    plt.legend(title="Architecture")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot to disk
    output_path = f"{output_dir_lambda}arch_v_m/mean_execution_time_by_architecture_and_memory_size.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

    print(f"Plot saved to {output_path}")

def calculate_cost(row):

    if row['architecture'] == 'x86':

        return row['billed_duration_ms'] * lambda_x86_pricing_per_ms[row['memory_size']]

    elif row['architecture'] == 'arm':

        return row['billed_duration_ms'] * lambda_arm_pricing_per_ms[row['memory_size']]

    return 0

def gen_architecture_cost_comparison(lambda_results_df: pd.DataFrame):
    # Relevant columns to work with
    relevant_columns = ['architecture', 'memory_size', 'billed_duration_ms']

    # Filter for relevant columns
    df_filtered = lambda_results_df[relevant_columns]

    # Add a cost column based on architecture and memory size
    df_filtered['cost'] = df_filtered.apply(calculate_cost, axis=1)

    # Compute the 2.5th and 97.5th percentiles for cost based on architecture and memory size
    percentiles = df_filtered.groupby(['architecture', 'memory_size'])['cost'].quantile([0.025, 0.975]).unstack()

    # Filter the data to keep only the middle 95% (between 2.5th and 97.5th percentiles)
    percentile_95_cost = df_filtered[
        df_filtered.apply(
            lambda row: percentiles.loc[row['architecture'], row['memory_size']][0.025] <= row['cost'] <= percentiles.loc[row['architecture'], row['memory_size']][0.975],
            axis=1
        )
    ]

    # Pivot for easier plotting
    cost_pivot = percentile_95_cost.pivot_table(index='memory_size', columns='architecture', values='cost', aggfunc='mean')

    # Calculate percentage difference (x86 vs ARM)
    cost_pivot['percent_diff'] = (
        (cost_pivot['x86'] - cost_pivot['arm']) / cost_pivot['x86'] * 100
    )

    # Plot the data
    bar_width = 0.35  # Width of the bars
    memory_sizes = cost_pivot.index
    x = np.arange(len(memory_sizes))  # X-axis positions

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars for each architecture
    ax.bar(x - bar_width / 2, cost_pivot['x86'], bar_width, label='x86', color='blue')
    ax.bar(x + bar_width / 2, cost_pivot['arm'], bar_width, label='ARM', color='orange')

    # Add percentage difference annotations above the bars
    for i, memory_size in enumerate(memory_sizes):
        percent_diff = cost_pivot.loc[memory_size, 'percent_diff']
        ax.text(
            x[i],  # X position
            max(cost_pivot.loc[memory_size, ['x86', 'arm']]),  # Y position (above the taller bar)
            f'{percent_diff:.1f}%',  # Format as percentage
            ha='center', va='bottom', fontsize=10, color='black'
        )

    # Add labels and legend
    ax.set_xlabel('Memory Size (MB)', fontsize=12)
    ax.set_ylabel('Mean Cost 1e-6 ($/ms)', fontsize=12)
    ax.set_title('Mean Cost of All Operations - Comparison by Architecture and Memory Size (95%)', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(memory_sizes)
    plt.legend(title="Architecture")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    # Save the plot to disk
    output_path = f"{output_dir_lambda}costs_all_arches_over_all_ops/mean_cost_by_architecture_and_memory_size.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

def gen_architecture_cost_comparison_by_operation_and_language(lambda_results_df: pd.DataFrame):
    # Filter relevant columns
    relevant_columns = ['architecture', 'memory_size', 'billed_duration_ms', 'operation', 'language']
    df_filtered = lambda_results_df[relevant_columns]

    # Add a cost column based on architecture and memory size
    df_filtered['cost'] = df_filtered.apply(calculate_cost, axis=1)

    # Iterate through each operation and language
    for operation in operations:
        for language in languages:
            # Filter data for the current operation and language
            df_subset = df_filtered[(df_filtered['operation'] == operation) & (df_filtered['language'] == language)]
            
            if df_subset.empty:
                continue  # Skip if no data for this combination



            # Step 3: Compute the 2.5th and 97.5th percentiles for cost based on architecture and memory size
            percentiles = df_filtered.groupby(['architecture', 'memory_size'])['cost'].quantile([0.025, 0.975]).unstack()

            # Step 4: Filter the data to keep only the middle 95% (between 2.5th and 97.5th percentiles)
            percentile_95_cost = df_filtered[
                df_filtered.apply(
                    lambda row: percentiles.loc[row['architecture'], row['memory_size']][0.025] <= row['cost'] <= percentiles.loc[row['architecture'], row['memory_size']][0.975],
                    axis=1
                )
            ]


            # Pivot the data for easier plotting
            cost_pivot = percentile_95_cost.pivot_table(index='memory_size', columns='architecture', values='cost', aggfunc='mean')

            # Calculate percentage difference (x86 vs ARM)
            cost_pivot['percent_diff'] = (
                (cost_pivot['x86'] - cost_pivot['arm']) / cost_pivot['x86'] * 100
            )

            # Plot the data
            bar_width = 0.35  # Width of the bars
            memory_sizes = cost_pivot.index
            x = np.arange(len(memory_sizes))  # X-axis positions

            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot bars for each architecture
            ax.bar(x - bar_width / 2, cost_pivot['x86'], bar_width, label='x86', color='blue')
            ax.bar(x + bar_width / 2, cost_pivot['arm'], bar_width, label='ARM', color='orange')

            # Add percentage difference annotations above the bars
            for i, memory_size in enumerate(memory_sizes):
                percent_diff = cost_pivot.loc[memory_size, 'percent_diff']
                ax.text(
                    x[i],  # X position
                    max(cost_pivot.loc[memory_size, ['x86', 'arm']]),  # Y position (above the taller bar)
                    f'{percent_diff:.1f}%',  # Format as percentage
                    ha='center', va='bottom', fontsize=10, color='black'
                )

            # Add labels, title, and legend
            ax.set_xlabel('Memory Size (MB)', fontsize=12)
            ax.set_ylabel('Mean Cost 1e-6 ($/ms)', fontsize=12)
            ax.set_title(f'{operation.capitalize()} ({language.capitalize()}) - Mean Cost by Architecture (95%)', fontsize=14)
            ax.set_xticks(x)
            ax.set_xticklabels(memory_sizes)
            plt.legend(title="Architecture")
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            plt.tight_layout()

            # Save the plot to disk
            output_path = f"{output_dir_lambda}cost_of_ops/{operation}_{language}_cost_comparison.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print("Done")

            # Optionally, show the plot
            plt.close(fig)

def analyze_lambda():
    aws_lambda_results_file_path = "cleaned-results-aws/Lambda-Results.csv"

    lambda_results_df = load_data(aws_lambda_results_file_path)
    save_architecture_comparison_heatmaps(lambda_results_df)
    save_operation_specific_heatmaps(lambda_results_df)

    #gen_blox_plots(lambda_results_df)
    #gen_bar_plots(lambda_results_df)
    #gen_architecture_comparison(lambda_results_df)
    #gen_architecture_cost_comparison(lambda_results_df)
    #gen_architecture_cost_comparison_by_operation_and_language(lambda_results_df)




if __name__ == "__main__":
    analyze_lambda()
    print("Analyzing Lambda Results.")
