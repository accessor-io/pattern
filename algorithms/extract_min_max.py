#!/usr/bin/env python3
"""
Extract minimum and maximum values from prediction files for the 68th term.
This script analyzes line_67s.txt and line_68s.txt to find valid value boundaries.
"""

import os
import logging
import sys

# Increase limit for integer string conversion
sys.set_int_max_str_digits(100000)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Known previous term (67)
PREV_TERM_67 = 0x730fc235c1942c1ae

def extract_values_from_file(filename):
    """
    Extract all valid integer values from a file.
    """
    values = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Convert hex string to integer
                        value = int(line, 16)
                        values.append(value)
                    except ValueError:
                        continue
    except FileNotFoundError:
        logger.warning(f"File {filename} not found")
    
    return values

def analyze_file(filename, filter_68_bits=False, filter_above_prev=False):
    """
    Analyze a file for min/max values and statistics.
    """
    values = extract_values_from_file(filename)
    
    if not values:
        logger.warning(f"No valid values found in {filename}")
        return None
    
    # Apply filters if requested
    if filter_68_bits:
        original_count = len(values)
        values = [v for v in values if v.bit_length() == 68]
        logger.info(f"Filtered for 68 bits: {len(values)}/{original_count} values remain")
    
    if filter_above_prev:
        original_count = len(values)
        values = [v for v in values if v > PREV_TERM_67]
        logger.info(f"Filtered for > prev term: {len(values)}/{original_count} values remain")
    
    if not values:
        logger.warning(f"No values remain after filtering for {filename}")
        return None
    
    # Find min/max values
    min_value = min(values)
    max_value = max(values)
    
    result = {
        "filename": filename,
        "count": len(values),
        "min_value": min_value,
        "min_value_hex": hex(min_value),
        "max_value": max_value,
        "max_value_hex": hex(max_value),
        "unique_values": len(set(values)),
        "filter_68_bits": filter_68_bits,
        "filter_above_prev": filter_above_prev
    }
    
    return result

def print_analysis(analysis):
    """
    Print the analysis results.
    """
    if not analysis:
        print("No analysis available")
        return
    
    print(f"\nAnalysis for: {analysis['filename']}")
    print(f"Total values: {analysis['count']} (unique: {analysis['unique_values']})")
    print(f"Min value: {analysis['min_value_hex']}")
    
    # For max value, only print hex to avoid huge decimal representation
    print(f"Max value (hex): {analysis['max_value_hex']}")
    
    # Print decimal for max only if it's reasonably sized
    if analysis['max_value'] < 1 << 200:  # arbitrary limit
        print(f"Max value (dec): {analysis['max_value']}")
    else:
        print(f"Max value (dec): [too large to display]")
    
    print(f"Filters applied: 68 bits={analysis['filter_68_bits']}, above prev={analysis['filter_above_prev']}")
    print("-" * 60)

def main():
    print("Analyzing prediction files for term 68 search...")
    print(f"Previous term (67): {hex(PREV_TERM_67)}")
    
    # Analyze line_67s.txt
    print("\n=== Analysis of term 67 values ===")
    analysis_67 = analyze_file("line_67s.txt")
    print_analysis(analysis_67)
    
    # Analyze line_68s.txt (all values)
    print("\n=== Analysis of all term 68 predictions ===")
    analysis_68_all = analyze_file("line_68s.txt")
    print_analysis(analysis_68_all)
    
    # Analyze line_68s.txt (only 68-bit values)
    print("\n=== Analysis of 68-bit term 68 predictions ===")
    analysis_68_filtered = analyze_file("line_68s.txt", filter_68_bits=True)
    print_analysis(analysis_68_filtered)
    
    # Analyze line_68s.txt (only valid candidates: 68-bit and > prev term)
    print("\n=== Analysis of valid term 68 candidates ===")
    analysis_68_valid = analyze_file("line_68s.txt", filter_68_bits=True, filter_above_prev=True)
    print_analysis(analysis_68_valid)
    
    # Calculate search range for valid 68-bit candidates
    print("\n=== Search Range Recommendations ===")
    print(f"Minimum value (Term 67+1): {hex(PREV_TERM_67 + 1)}")
    
    if analysis_68_valid:
        print(f"Predicted minimum: {analysis_68_valid['min_value_hex']}")
        print(f"Predicted maximum: {analysis_68_valid['max_value_hex']}")
    
    print(f"Maximum 68-bit value: {hex((1 << 68) - 1)}")
    
    # Additional recommendations
    print("\n=== Search Recommendations ===")
    print("1. Focus on sequences where term 68 = term 67 × constant")
    print("2. Try bit-flipping operations on promising candidates")
    print("3. Explore values near term 67 + significant bit shifts")
    print(f"4. Check values around {hex(PREV_TERM_67 + (PREV_TERM_67 >> 4))}")
    print("5. Explore mathematical patterns (Fibonacci, golden ratio, etc.)")

if __name__ == "__main__":
    main() 