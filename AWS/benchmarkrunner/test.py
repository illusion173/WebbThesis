import psutil
import subprocess
import time
import os

# External command to execute (replace with your actual executable command)
command = ["cat "]  # Replace with actual command and args
dir = "../../TestArtifacts/inputs/sha256.json"
# Start time
start_time = time.time()

# Start the external process using subprocess
process = subprocess.Popen(command)

# Get the PID of the subprocess
pid = process.pid

# Use psutil to monitor the subprocess
ps_process = psutil.Process(pid)

# Initial memory usage (before execution starts)
initial_memory = ps_process.memory_info().rss / (1024 * 1024)  # Memory in MB

# Wait for the process to complete
process.wait()

# End time
end_time = time.time()

# Final memory usage (after execution ends)
final_memory = ps_process.memory_info().rss / (1024 * 1024)  # Memory in MB

# Calculate execution time
execution_time = end_time - start_time

# Output results
print(f"Execution Time: {execution_time:.4f} seconds")
print(f"Initial Memory Usage: {initial_memory:.2f} MB")
print(f"Final Memory Usage: {final_memory:.2f} MB")
print(f"Memory Usage Increased by: {final_memory - initial_memory:.2f} MB")
