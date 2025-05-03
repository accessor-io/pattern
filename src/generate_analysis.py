 #!/usr/bin/python3

import os
from run_all_analyses import read_hex_strings, ensure_output_dir, write_analysis

def main():
    """Main function to run all analyses"""
    # Ensure input file exists
    input_file = 'data/32bHex.txt'
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return

    # Create output directory if it doesn't exist
    ensure_output_dir()

    # Read hex strings
    hex_strings = read_hex_strings(input_file)
    if not hex_strings:
        print("Error: No hex strings found in input file")
        return

    # Generate complete analysis
    with open('output/complete_analysis.txt', 'w') as outfile:
        outfile.write("256-bit Pattern Analysis\n")
        outfile.write("=" * 80 + "\n\n")
        
        for i, hex_string in enumerate(hex_strings, 1):
            write_analysis(hex_string, i, outfile)
            print(f"Completed analysis for string {i} of {len(hex_strings)}")

    print("\nAnalysis complete. Results written to output/complete_analysis.txt")

if __name__ == "__main__":
    main() 