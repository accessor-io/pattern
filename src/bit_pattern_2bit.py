#!/usr/bin/python3

import subprocess
import os

def read_hex_strings(filename):
    """Read and clean hex strings from file"""
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def validate_hex_string(hex_string):
    """Validate hex string is exactly 64 characters (32 bytes)"""
    if len(hex_string) > 64:
        raise ValueError(f"Hex string too long: {len(hex_string)} chars. Must be 64 chars.")
    return hex_string.zfill(64)  # Pad shorter strings to 64 chars

def hex_to_2bit_patterns(hex_string):
    """Convert hex string to 2-bit patterns"""
    # Validate and pad to exactly 32 bytes (64 hex chars)
    hex_string = validate_hex_string(hex_string)
    
    # Convert to binary
    num = int(hex_string, 16)
    binary = format(num, '0256b')  # Ensure exactly 256 bits
    
    # Group into 2-bit patterns and track positions
    two_bit_patterns = []
    pattern_positions = {'00': [], '01': [], '10': [], '11': []}
    
    for i in range(0, 256, 2):
        pattern = binary[i:i+2]
        two_bit_patterns.append(pattern)
        pattern_positions[pattern].append(i//2)  # Store position of each pattern
    
    return {
        'binary': binary,
        'patterns': two_bit_patterns,
        'positions': pattern_positions,
        'hex': hex_string
    }

def format_2bit_patterns(patterns, patterns_per_line=16):
    """Format 2-bit patterns into readable lines with position markers"""
    formatted_lines = []
    for i in range(0, len(patterns), patterns_per_line):
        chunk = patterns[i:i+patterns_per_line]
        pos_start = i * 2
        pos_end = (i + len(chunk)) * 2 - 1
        # Add position markers for each pattern
        patterns_with_pos = []
        for j, pattern in enumerate(chunk):
            pos = i + j
            patterns_with_pos.append(f"{pattern}")
        line = f"[{i//patterns_per_line:2d}] {pos_start:3d}-{pos_end:<3d}: {' '.join(patterns_with_pos)}"
        formatted_lines.append(line)
    return formatted_lines

def process_file(filename):
    try:
        print(f"Reading from: {filename}")
        hex_strings = read_hex_strings(filename)
        print(f"Processing {len(hex_strings)} hex strings")
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        output_filename = 'output/256bit_patterns.txt'
        with open(output_filename, 'w') as outfile:
            outfile.write("256-bit Pattern Analysis (2-bit groupings)\n")
            outfile.write("=" * 70 + "\n\n")
            
            for i, hex_string in enumerate(hex_strings, 1):
                try:
                    pattern_data = hex_to_2bit_patterns(hex_string)
                    
                    # Write header for this string
                    outfile.write(f"String {i}:\n")
                    outfile.write(f"Hex: {pattern_data['hex']}\n\n")
                    
                    # Write 2-bit pattern analysis
                    outfile.write("2-bit patterns across 256 bits:\n")
                    formatted_patterns = format_2bit_patterns(pattern_data['patterns'])
                    outfile.write("\n".join(formatted_patterns) + "\n\n")
                    
                    # Write pattern statistics and positions
                    outfile.write("Pattern analysis:\n")
                    for pattern in ['00', '01', '10', '11']:
                        positions = pattern_data['positions'][pattern]
                        count = len(positions)
                        outfile.write(f"{pattern}: {count:3d} occurrences ({count/128*100:5.1f}%)\n")
                        if count > 0:
                            outfile.write(f"     Positions: {positions}\n")
                    
                    outfile.write("\n" + "-" * 70 + "\n\n")
                
                except ValueError as ve:
                    outfile.write(f"Error in string {i}: {str(ve)}\n\n")
        
        print(f"256-bit patterns saved to: {output_filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main function to analyze 2-bit patterns"""
    process_file("../data/32bHex.txt")

if __name__ == "__main__":
    main() 