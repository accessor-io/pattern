import collections
import sys


def analyze_ascii_file(input_file: str = "ascii_keys.txt"):
    """Analyze the ASCII conversion outputs from the given file and print statistics."""
    try:
        with open(input_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run write_ascii.py first.")
        return

    ascii_outputs = []
    for line in lines:
        if "=> ASCII:" in line:
            parts = line.strip().split("=> ASCII:")
            if len(parts) == 2:
                ascii_str = parts[1].strip()
                ascii_outputs.append(ascii_str)

    total_keys = len(ascii_outputs)
    if total_keys == 0:
        print("No ASCII outputs found in the file.")
        return

    # Count frequency of each character across all ascii outputs
    frequency = collections.Counter("".join(ascii_outputs))

    # Count lines that are entirely dots (useful as an indicator of non-printable results)
    count_all_dots = sum(1 for s in ascii_outputs if all(ch == '.' for ch in s) and s != "")

    # Calculate average length of ASCII outputs
    avg_length = sum(len(s) for s in ascii_outputs) / total_keys
    
    print(f"Total keys analyzed: {total_keys}")
    print("\nFrequency of ASCII characters in all outputs:")
    for char, count in frequency.most_common():
        # For readability, replace dot with literal '.' in output
        display_char = char if char != ' ' else "<space>"
        print(f"'{display_char}': {count}")
    
    print(f"\nNumber of keys with output entirely non-printable (all dots): {count_all_dots}")
    print(f"Average length of ASCII conversion outputs: {avg_length:.2f}")


if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else "ascii_keys.txt"
    analyze_ascii_file(input_file) 