# Define the filename
filename = "10kb_file.txt"

# Define the size of the file in KB (10 KB = 10 * 1024 bytes)
file_size = 10 * 1024  # 10 KB in bytes

# Create the content to write (we can write repeated characters to meet the size)
content = "A" * file_size  # 10 KB of 'A' characters

# Write the content to the file
with open(filename, "w") as f:
    f.write(content)

print(f"{filename} has been created with {file_size} bytes (10 KB).")
