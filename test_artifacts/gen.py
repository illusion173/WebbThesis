def create_file(filename, size_kb):
    with open(filename, 'w', encoding='utf-8') as f:
        text = "Thisisasamplelineoftext" * (size_kb * 1024 // len("Thisisasamplelineoftext"))
        f.write(text[:size_kb * 1024])  # Trim to exact size

# Generate files
create_file('1KB.txt', 1)
create_file('10KB.txt', 10)
create_file('1MB.txt', 1024)
