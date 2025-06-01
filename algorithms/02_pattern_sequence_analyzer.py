#!/usr/bin/env python3
"""
02_pattern_sequence_analyzer.py - Hex Sequence Pattern Analyzer

A specialized tool for analyzing sequences of hexadecimal values from files.
This analyzer reads hex sequences and performs detailed statistical analysis
of their properties, focusing on cryptographic characteristics and security metrics.

Features:
- File-based hex sequence input processing
- Statistical analysis of sequence properties
- Bit pattern and block pattern analysis
- Security property assessment with detailed reporting
- Comprehensive metrics visualization and summarization

Applications:
- Cryptographic sequence quality assessment
- Bitcoin address generation evaluation
- Randomness validation for key sequences
- Security evaluation for cryptographic algorithms
"""

import sys
from algorithms.sequence.analyzers.01_sequence_analyzer import SequenceAnalyzer

def read_hex_sequence(filename: str) -> list:
    """
    Reads a sequence of hex values from a file.
    Each value should be on a new line, with optional '0x' prefix.
    """
    values = []
    with open(filename, 'r') as f:
        for line in f:
            # Clean the line and remove any '0x' prefix
            clean_line = line.strip().replace('0x', '')
            if clean_line:
                try:
                    value = int(clean_line, 16)
                    values.append(value)
                except ValueError as e:
                    print(f"Warning: Skipping invalid hex value: {line.strip()}")
    return values

def analyze_sequence_file(filename: str, block_size: int = 4):
    """
    Reads and analyzes a sequence from a file.
    """
    # Read the sequence
    try:
        values = read_hex_sequence(filename)
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not values:
        print("Error: No valid values found in file")
        return

    # Create analyzer and run analysis
    analyzer = SequenceAnalyzer(values)
    
    # Run all analyses
    differences = analyzer.analyze_consecutive_differences()
    bit_patterns = analyzer.analyze_bit_patterns()
    block_patterns = analyzer.analyze_block_patterns(block_size)
    security = analyzer.analyze_security_properties()
    
    # Print detailed results
    print("\n=== Sequence Analysis Results ===")
    print(f"\nAnalyzing {len(values)} values from {filename}")
    
    print("\n1. Value Statistics:")
    print(f"First value: {hex(values[0])}")
    print(f"Last value: {hex(values[-1])}")
    print(f"Total values: {len(values)}")
    
    print("\n2. Consecutive Differences:")
    print(f"Mean difference: {differences['mean']:.2f}")
    print(f"Min difference: {differences['min']}")
    print(f"Max difference: {differences['max']}")
    print(f"Standard deviation: {differences['std_dev']:.2f}")
    
    print("\n3. Bit Pattern Analysis:")
    total_changes = sum(p['bit_changes'] for p in bit_patterns)
    avg_changes = total_changes / len(bit_patterns)
    print(f"Average bit changes: {avg_changes:.2f}")
    print(f"Total bit changes: {total_changes}")
    print("\nDetailed bit changes:")
    for pattern in bit_patterns[:5]:  # Show first 5 transitions
        print(f"Position {pattern['position']}:")
        print(f"  {pattern['prev_value']} -> {pattern['curr_value']}")
        print(f"  Changes: {pattern['bit_changes']} bits")
        print(f"  Hamming weight change: {pattern['hamming_weight_change']}")
    if len(bit_patterns) > 5:
        print("... (showing first 5 transitions only)")
    
    print("\n4. Block Pattern Analysis:")
    print(f"Block size: {block_size} bits")
    for pattern in block_patterns[:3]:  # Show first 3 positions
        print(f"\nPosition {pattern['position']}:")
        for block in pattern['block_changes'][:3]:  # Show first 3 blocks
            print(f"  Block {block['block_position']}:")
            print(f"    {block['prev_block']} -> {block['curr_block']}")
            print(f"    Changes: {block['changes']} bits")
    if len(block_patterns) > 3:
        print("... (showing first 3 positions only)")
    
    print("\n5. Security Properties:")
    print(f"Rate-α: {security['rate_alpha']:.3f}")
    print(f"Average bit changes: {security['avg_bit_changes']:.2f}")
    print(f"Avalanche quality: {security['avalanche_quality']:.2f}")
    print(f"Estimated minimum permutations: {security['permutation_estimate']}")
    
    # Print summary
    print("\n=== Analysis Summary ===")
    print(f"Sequence length: {len(values)}")
    print(f"Rate-α: {security['rate_alpha']:.3f} (should be < 0.5)")
    print(f"Avalanche quality: {security['avalanche_quality']:.2f} (ideal = 1.0)")
    print(f"Security assessment: {'✓ SATISFACTORY' if security['rate_alpha'] < 0.5 else '✗ NEEDS IMPROVEMENT'}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python 02_pattern_sequence_analyzer.py <hex_sequence_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_sequence_file(filename)

if __name__ == "__main__":
    main() 