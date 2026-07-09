import sys
sys.path.insert(0, '.')

from src.standard.pipeline import main
input_data=""

# Read the entire file content into one string
file_path = "C:/AI/T1.txt"

with open(file_path, "r", encoding="utf-8") as file:
    input_data = file.read()

if __name__ == "__main__":
    sys.argv = ["pipeline", "--input", input_data]
    main()