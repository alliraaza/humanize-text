"""Example: Run the Standard humanization pipeline."""

import sys
import toml
from pathlib import Path
from src.standard import run_standard_pipeline

from datetime import datetime

# Check if the user passed an argument
if len(sys.argv) < 2:
        print("Usage: python run.py <filename>")
        sys.exit(1)

file_path = sys.argv[1]

# Capture the exact start time
start_time = datetime.now()

# Print formatted as YYYY-MM-DD HH:MM:SS
print(f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

config = toml.load("config/config.toml")

# Read the entire file content into one string
# file_path = "C:/AI/T2-400W.txt"
print(f"Processing file: {file_path}")

input_path = Path(file_path)

# Check if the file exists before proceeding
if not input_path.exists():
    print(f"❌ Error: File '{input_path}' not found.")
    sys.exit(1)
else:
    output_path = input_path.with_stem(f"{input_path.stem}_hm")

try:
    with open(file_path, "r", encoding="utf-8") as file:
        input_data = file.read()
except FileNotFoundError:
    print(f"Error: The file '{file_path}' does not exist.")
word_count = len(input_data.split())
print(f"Original word count: {word_count}")

result = run_standard_pipeline(input_data, config, target_lang="en")

output= result["result"]
word_count = len(output.split())
print(f"Output word count: {word_count}")


print(f"\nProcessing time: {result['processing_time_ms']}ms")
print("\nSteps:")
for step in result["steps"]:
    print(f"  {step['step']}: {step['engine']} | {step['direction']} | {step['length']} chars")


    # 4. Write to the new _out file in the exact same directory
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(output)

    print(f"✅ Success! Saved output to: {output_path}")

start_time = datetime.now()
print(f"Script finished at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
