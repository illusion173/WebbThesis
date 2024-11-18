import pandas as pd
import matplotlib.pyplot as plt

class BenchmarkVisualizer:
    def __init__(self, csv_file):
        """
        Initialize the BenchmarkVisualizer with the given CSV file.
        
        :param csv_file: Path to the CSV file containing benchmark results.
        """
        self.csv_file = csv_file
        self.df = None

    def load_data(self):
        """
        Loads the data from the CSV file into a pandas DataFrame.
        """
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"Data loaded successfully from {self.csv_file}")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def process_data(self):
        """
        Process the loaded data by filtering for 'sha384' operations,
        grouping by language and start_type, and calculating the mean execution time,
        CPU usage, and memory usage for each combination.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")
        
        # Filter data for only 'sha384' operations
        sha384_df = self.df[self.df['operation'] == 'sha384']
        
        # Group by 'language' and 'start_type', and compute the average execution time, CPU usage, and memory usage
        df_grouped = sha384_df.groupby(['language', 'start_type']).agg(
            avg_execution_time_ms=('execution_time_ms', 'mean'),
            avg_cpu_usage_percent=('avg_cpu_usage_percent', 'mean'),
            avg_memory_usage_mb=('avg_memory_usage_mb', 'mean')
        ).reset_index()

        # Pivot the data to have 'start_type' as columns for execution time, CPU usage, and memory usage
        df_pivot_exec_time = df_grouped.pivot(index='language', columns='start_type', values='avg_execution_time_ms')
        df_pivot_cpu_usage = df_grouped.pivot(index='language', columns='start_type', values='avg_cpu_usage_percent')
        df_pivot_mem_usage = df_grouped.pivot(index='language', columns='start_type', values='avg_memory_usage_mb')

        return df_pivot_exec_time, df_pivot_cpu_usage, df_pivot_mem_usage

    def plot_and_save(self, df_pivot_exec_time, df_pivot_cpu_usage, df_pivot_mem_usage):
        """
        Plots dual bar graphs for execution time, CPU usage, and memory usage comparison 
        based on programming language and start type (cold vs. warm start).
        Saves each plot as a PNG file.
        
        :param df_pivot_exec_time: DataFrame with pivoted execution time data.
        :param df_pivot_cpu_usage: DataFrame with pivoted CPU usage data.
        :param df_pivot_mem_usage: DataFrame with pivoted memory usage data.
        """
        # Define filenames for the output images
        filenames = {
            'execution_time': 'sha384_execution_time_by_language.png',
            'cpu_usage': 'sha384_cpu_usage_by_language.png',
            'memory_usage': 'sha384_memory_usage_by_language.png'
        }

        # Plot for Execution Time
        plt.figure(figsize=(10, 6))
        df_pivot_exec_time.plot(kind='bar', width=0.8)
        plt.title('SHA384 Execution Time by Programming Language and Start Type')
        plt.xlabel('Programming Language')
        plt.ylabel('Execution Time (ms)')
        plt.xticks(rotation=45)
        plt.legend(title='Start Type')
        plt.tight_layout()
        plt.savefig(filenames['execution_time'])
        print(f"Saved execution time plot as {filenames['execution_time']}")
        plt.close()

        # Plot for CPU Usage
        plt.figure(figsize=(10, 6))
        df_pivot_cpu_usage.plot(kind='bar', width=0.8, color=['#ff9999', '#66b3ff'])
        plt.title('SHA384 CPU Usage by Programming Language and Start Type')
        plt.xlabel('Programming Language')
        plt.ylabel('Average CPU Usage (%)')
        plt.xticks(rotation=45)
        plt.legend(title='Start Type')
        plt.tight_layout()
        plt.savefig(filenames['cpu_usage'])
        print(f"Saved CPU usage plot as {filenames['cpu_usage']}")
        plt.close()

        # Plot for Memory Usage
        plt.figure(figsize=(10, 6))
        df_pivot_mem_usage.plot(kind='bar', width=0.8, color=['#99ff99', '#ffcc99'])
        plt.title('SHA384 Memory Usage by Programming Language and Start Type')
        plt.xlabel('Programming Language')
        plt.ylabel('Average Memory Usage (MB)')
        plt.xticks(rotation=45)
        plt.legend(title='Start Type')
        plt.tight_layout()
        plt.savefig(filenames['memory_usage'])
        print(f"Saved memory usage plot as {filenames['memory_usage']}")
        plt.close()

def main():
    # Path to the CSV file containing benchmark results (replace with actual path)
    csv_file = 'x86_64-TEST-AWSEC2-Benchmarkresults.csv'

    # Initialize the BenchmarkVisualizer object
    visualizer = BenchmarkVisualizer(csv_file)

    # Load the data from the CSV file
    visualizer.load_data()

    # Process the data to group and pivot it
    df_pivot_exec_time, df_pivot_cpu_usage, df_pivot_mem_usage = visualizer.process_data()

    # Plot the data and save as PNG files
    visualizer.plot_and_save(df_pivot_exec_time, df_pivot_cpu_usage, df_pivot_mem_usage)

# Run the main function if this script is executed
if __name__ == "__main__":
    main()
