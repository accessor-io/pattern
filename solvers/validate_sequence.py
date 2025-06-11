#!/usr/bin/env python3
from archive.known_keys import KNOWN_KEYS

def load_generated_sequence(filename="generated_sequence_160.txt"):
    """Load the generated sequence from a file"""
    sequence = {}
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f, 1):
                sequence[i] = int(line.strip(), 16)
        return sequence
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return None

def validate_known_keys(sequence):
    """Validate that the sequence matches all known keys"""
    if not sequence:
        return False
    
    print("Validating sequence against known keys...")
    
    mismatches = []
    for i in KNOWN_KEYS:
        if i not in sequence or sequence[i] != KNOWN_KEYS[i]:
            mismatches.append(i)
    
    if mismatches:
        print(f"❌ Found {len(mismatches)} mismatches at positions: {mismatches}")
        return False
    else:
        print(f"✅ All {len(KNOWN_KEYS)} known keys match!")
        return True

def validate_xor_pattern(sequence):
    """Validate that the XOR pattern between consecutive keys is consistent"""
    print("\nAnalyzing XOR patterns between consecutive keys...")
    
    xor_patterns = []
    for i in range(1, max(sequence.keys())):
        if i+1 in sequence:
            xor_val = sequence[i+1] ^ sequence[i]
            bit_count = bin(xor_val).count('1')
            xor_patterns.append((xor_val, bit_count))
    
    # Check for sudden jumps in bit count
    abnormal_jumps = []
    for i in range(1, len(xor_patterns)):
        prev_bits = xor_patterns[i-1][1]
        curr_bits = xor_patterns[i][1]
        
        if abs(curr_bits - prev_bits) > 10:  # Threshold for suspicious jump
            abnormal_jumps.append((i, prev_bits, curr_bits))
    
    if abnormal_jumps:
        print(f"⚠️ Found {len(abnormal_jumps)} suspicious bit count jumps:")
        for pos, prev, curr in abnormal_jumps:
            print(f"  Position {pos+1}: {prev} → {curr} bits (+{curr-prev})")
    else:
        print("✅ XOR bit counts follow a smooth pattern")
    
    # Calculate average bit growth
    avg_growth = sum(xor_patterns[i][1] - xor_patterns[i-1][1] 
                     for i in range(1, len(xor_patterns))) / (len(xor_patterns) - 1)
    print(f"Average bit growth between consecutive keys: {avg_growth:.2f}")
    
    return True

def validate_bit_count_growth(sequence):
    """Validate that the bit count growth follows the expected pattern"""
    print("\nChecking bit count growth pattern...")
    
    # Calculate bit counts for all keys
    bit_counts = {i: bin(val).count('1') for i, val in sequence.items()}
    
    # Check if bit counts follow the expected pattern
    expected_pattern = True
    anomalies = []
    
    for i in range(2, max(sequence.keys())):
        # For positions <= 7, bit count should increase by ~1
        if i <= 8:
            expected_diff = 1
            tolerance = 2
        else:
            # For later positions, we expect more variation but still some coherence
            expected_diff = 2
            tolerance = 6
        
        actual_diff = bit_counts[i] - bit_counts[i-1]
        if abs(actual_diff) > tolerance:
            anomalies.append((i, actual_diff))
            expected_pattern = False
    
    if expected_pattern:
        print("✅ Bit count growth follows the expected pattern")
    else:
        print(f"⚠️ Found {len(anomalies)} unexpected bit count changes:")
        for pos, diff in anomalies[:5]:  # Show first 5 anomalies
            print(f"  Position {pos}: Change of {diff} bits (expected ±{expected_diff})")
        if len(anomalies) > 5:
            print(f"  ... and {len(anomalies) - 5} more")
    
    return expected_pattern

def check_key_size_growth(sequence):
    """Check how the key byte size grows with position"""
    print("\nAnalyzing key size growth...")
    
    # Group keys by their hex length
    length_groups = {}
    for i, val in sequence.items():
        hex_len = len(hex(val)[2:])
        if hex_len not in length_groups:
            length_groups[hex_len] = []
        length_groups[hex_len].append(i)
    
    # Print summary of key sizes
    print(f"Key lengths found in sequence:")
    for hex_len in sorted(length_groups.keys()):
        positions = length_groups[hex_len]
        print(f"  {hex_len} hex digits: {len(positions)} keys (e.g., positions {positions[:3]}{'...' if len(positions) > 3 else ''})")
    
    # Find the largest key size
    max_size = max(length_groups.keys())
    max_size_pos = min(length_groups[max_size])
    print(f"Maximum key size: {max_size} hex digits at position {max_size_pos}")
    
    return True

if __name__ == "__main__":
    # Load the generated sequence
    sequence = load_generated_sequence()
    if not sequence:
        exit(1)
    
    print(f"Loaded sequence with {len(sequence)} keys\n")
    
    # Run validation checks
    validate_known_keys(sequence)
    validate_xor_pattern(sequence)
    validate_bit_count_growth(sequence)
    check_key_size_growth(sequence)
    
    print("\nValidation complete!") 