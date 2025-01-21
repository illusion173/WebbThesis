import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load CSV data
def load_data(file_path):
    """Load benchmark data from a CSV file."""
    return pd.read_csv(file_path)

# Statistical summary
def summarize_data(df):
    """Return descriptive statistics for numerical columns."""
    return df.describe()

# Plot execution time distribution
def plot_execution_time_distribution(df):
    """Plot the distribution of execution times."""
    plt.figure(figsize=(10, 6))
    sns.histplot(df['execution_time_ms'], kde=True, bins=30, color='blue')
    plt.title('Distribution of Execution Times (ms)')
    plt.xlabel('Execution Time (ms)')
    plt.ylabel('Frequency')
    plt.show()

# Compare execution time by memory size
def compare_execution_time_by_memory(df):
    """Compare average execution times across memory sizes."""
    avg_execution = df.groupby('memory_size')['execution_time_ms'].mean()
    plt.figure(figsize=(10, 6))
    avg_execution.plot(kind='bar', color='orange')
    plt.title('Average Execution Time by Memory Size')
    plt.xlabel('Memory Size (MB)')
    plt.ylabel('Average Execution Time (ms)')
    plt.xticks(rotation=45)
    plt.show()

# Compare combinations
def compare_combinations(df):
    """Compare execution times across different combinations."""
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        data=df,
        x='memory_size',
        y='execution_time_ms',
        hue='start_type'
    )
    plt.title('Execution Time by Memory Size and Start Type')
    plt.xlabel('Memory Size (MB)')
    plt.ylabel('Execution Time (ms)')
    plt.legend(title='Start Type')
    plt.show()

# Filter by attributes
def filter_combinations(df, architecture=None, language=None, operation=None, start_type=None, memory_size=None):
    """Filter the DataFrame by specified attributes."""
    filtered_df = df.copy()

    if architecture:
        filtered_df = filtered_df[filtered_df['architecture'] == architecture]
    if language:
        filtered_df = filtered_df[filtered_df['language'] == language]
    if operation:
        filtered_df = filtered_df[filtered_df['operation'] == operation]
    if start_type:
        filtered_df = filtered_df[filtered_df['start_type'] == start_type]
    if memory_size:
        filtered_df = filtered_df[filtered_df['memory_size'] == memory_size]

    return filtered_df

# Correlation heatmap
def plot_correlation_heatmap(df):
    """Plot a heatmap of correlations between numerical variables."""
    plt.figure(figsize=(10, 8))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.show()

# Outlier detection
def detect_outliers(df, column, threshold=3):
    """Detect outliers in a column using z-scores."""
    mean = df[column].mean()
    std = df[column].std()
    df['z_score'] = (df[column] - mean) / std
    outliers = df[np.abs(df['z_score']) > threshold]
    return outliers

# Main execution
if __name__ == "__main__":
    # Load the dataset
    file_path = "cleaned-results-aws/Lambda-Results.csv"
    df = load_data(file_path)

    # Summarize data
    print("Statistical Summary:")
    print(summarize_data(df))

    # Plot execution time distribution
    plot_execution_time_distribution(df)

    # Compare execution time by memory size
    compare_execution_time_by_memory(df)

    # Compare combinations
    compare_combinations(df)

    # Filter specific combinations and display
    filtered = filter_combinations(df, architecture='x86', language='c#', operation='sha256', start_type='cold', memory_size=512)
    print("Filtered Data:")
    print(filtered)

    # Plot correlation heatmap
    #plot_correlation_heatmap(df)

    # Detect and print outliers for execution time
    outliers = detect_outliers(df, 'execution_time_ms')
    print("Outliers in Execution Time:")
    print(outliers)
