"""Example: Run the Standard humanization pipeline."""

import sys
import toml
from pathlib import Path
from src.standard import run_standard_pipeline

import time
from rich.console import Console

from datetime import datetime

# Check if the user passed an argument
if len(sys.argv) < 2:
        print("Usage: python run.py <filename>")
        sys.exit(1)

file_path = sys.argv[1]

# Capture the exact start time
start_time = datetime.now()

# Print formatted as YYYY-MM-DD HH:MM:SS
print(f"\n⏳ Process started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
config = toml.load("config/config.toml")
print(f"📄 Loaded file: {file_path}")

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

print(f"\n💡 Original file word count: {word_count}")

console = Console()

# The spinner stays active as long as code is inside this block
with console.status("\n[bold green]🤖 Running AI rewrite...", spinner="dots"):
    result = run_standard_pipeline(input_data, config, target_lang="en")
console.print("\n✅ [bold white]Finished AI rewrite![/bold white]")
output= result["result"]
word_count = len(output.split())
print(f"\n💡 Output file word count: {word_count}")


print(f"\n⏱️ AI Processing time: {result['processing_time_ms']}ms")

# 4. Write to the new _out file in the exact same directory
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.write(output)


print(f"\n🎯 Success! Job done. Saved output to: {output_path}")

print("\nSteps:")
for step in result["steps"]:
    print(f"☑️  {step['step']}: {step['engine']} | {step['direction']} | {step['length']} chars")

end_time = datetime.now()

elapsed_time = end_time - start_time

print(f"\n⏱️ Total Elapsed seconds: {elapsed_time.total_seconds():.2f}s")
