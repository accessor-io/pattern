#!/usr/bin/env python3

from sequence_analyzer import SequenceAnalyzer

def main():
    # Read the sequence from file
    with open('sequence.txt', 'r') as f:
        values = [int(line.strip().replace('0x', ''), 16) for line in f if line.strip()]
    
    # Create analyzer
    analyzer = SequenceAnalyzer(values)
    
    # Run analysis
    differences = analyzer.analyze_consecutive_differences()
    bit_patterns = analyzer.analyze_bit_patterns()
    block_patterns = analyzer.analyze_block_patterns(4)
    security = analyzer.analyze_security_properties()
    
    # Print results
    print("\n=== Sequence Analysis Results ===")
    
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
    for pattern in bit_patterns:
        print(f"\nPosition {pattern['position']}:")
        print(f"  {pattern['prev_value']} -> {pattern['curr_value']}")
        print(f"  Changes: {pattern['bit_changes']} bits")
        print(f"  Hamming weight change: {pattern['hamming_weight_change']}")
    
    print("\n4. Security Properties:")
    print(f"Rate-α: {security['rate_alpha']:.3f}")
    print(f"Average bit changes: {security['avg_bit_changes']:.2f}")
    print(f"Avalanche quality: {security['avalanche_quality']:.2f}")
    print(f"Estimated permutations: {security['permutation_estimate']}")

if __name__ == "__main__":
    main() 