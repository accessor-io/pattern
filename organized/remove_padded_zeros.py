#!/usr/bin/env python3
"""
Script to remove padded zeros from hexadecimal values in a file.
"""

def remove_padded_zeros(input_file, output_file):
    """
    Read the input file, remove padded zeros from each line,
    and write the result to the output file.
    """
    with open(input_file, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            for line in f_in:
                # Strip whitespace and convert to integer to remove leading zeros
                hex_value = line.strip()
                if hex_value:
                    # Convert to integer and back to hex to remove leading zeros
                    int_value = int(hex_value, 16)
                    clean_hex = hex(int_value)[2:]  # Remove '0x' prefix
                    f_out.write(clean_hex + '\n')

if __name__ == "__main__":
    input_file = "organized/data/utf8_bytes.txt"
    output_file = "organized/data/clean_utf8_bytes.txt"
    remove_padded_zeros(input_file, output_file)
    print(f"Processed {input_file} and saved results to {output_file}") 