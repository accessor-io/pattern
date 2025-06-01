#!/usr/bin/env python3
"""Analyze complex patterns for positions 30-68 where k + constant fails"""

def analyze_complex_patterns():
    """Analyze positions 30-68 to find the complex mathematical patterns"""
    
    # Load known sequence from verified file
    verified_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                else:
                    hex_key = hex_and_status.strip()
                verified_keys[pos] = int(hex_key, 16)
                
        print(f"✓ Loaded {len(verified_keys)} verified keys")
        
    except Exception as e:
        print(f"✗ Error reading verified sequence: {e}")
        return
    
    print(f"\n=== ANALYZING COMPLEX PATTERNS (Positions 30-68) ===")
    
    # Analyze the transition from simple to complex
    print(f"\n--- Pattern Transition Analysis ---")
    simple_range = range(25, 30)  # Last few simple positions
    complex_range = range(30, 35)  # First few complex positions
    
    print("Simple pattern (positions 25-29):")
    for pos in simple_range:
        if pos in verified_keys and pos-1 in verified_keys:
            diff = verified_keys[pos] - verified_keys[pos-1]
            print(f"  {pos-1}→{pos}: {diff:,}")
    
    print("\nComplex pattern (positions 30-34):")
    for pos in complex_range:
        if pos in verified_keys and pos-1 in verified_keys:
            diff = verified_keys[pos] - verified_keys[pos-1]
            ratio = diff / verified_keys[pos-1] if verified_keys[pos-1] > 0 else 0
            print(f"  {pos-1}→{pos}: {diff:,} (ratio: {ratio:.3f})")
    
    # Test different mathematical operations for complex positions
    print(f"\n=== TESTING COMPLEX FORMULAS ===")
    
    # Test positions 30-68 with various mathematical operations
    for pos in range(30, min(69, max(verified_keys.keys()) + 1)):
        if pos not in verified_keys or pos-1 not in verified_keys:
            continue
            
        current_key = verified_keys[pos-1]
        target_key = verified_keys[pos]
        
        print(f"\n--- Position {pos-1} → {pos} ---")
        print(f"Current: 0x{current_key:x} ({current_key:,})")
        print(f"Target:  0x{target_key:x} ({target_key:,})")
        
        # Test various mathematical operations
        formulas_to_test = []
        
        # Exponential patterns
        for base in [2, 3, 5, 7, 10]:
            for exp in range(1, 20):
                result = current_key + pow(base, exp)
                if result == target_key:
                    formulas_to_test.append(f"k + {base}^{exp}")
                
                result = current_key * pow(base, exp)
                if result == target_key:
                    formulas_to_test.append(f"k * {base}^{exp}")
        
        # Bitshift patterns
        for shift in range(1, 64):
            # Left shifts
            result = current_key + (current_key << shift)
            if result == target_key:
                formulas_to_test.append(f"k + (k << {shift})")
                
            result = current_key << shift
            if result == target_key:
                formulas_to_test.append(f"k << {shift}")
                
            # Combined shifts
            result = (current_key << shift) + current_key
            if result == target_key:
                formulas_to_test.append(f"(k << {shift}) + k")
                
            result = (current_key << shift) - current_key
            if result == target_key:
                formulas_to_test.append(f"(k << {shift}) - k")
        
        # Position-based patterns
        for mult in range(1, 100):
            result = current_key + (pos * mult)
            if result == target_key:
                formulas_to_test.append(f"k + pos * {mult}")
                
            result = current_key * mult
            if result == target_key:
                formulas_to_test.append(f"k * {mult}")
        
        # Power patterns with position
        for exp in range(2, 10):
            result = current_key + pow(pos, exp)
            if result == target_key:
                formulas_to_test.append(f"k + pos^{exp}")
                
            result = current_key * pow(pos, exp)
            if result == target_key:
                formulas_to_test.append(f"k * pos^{exp}")
        
        # Square and higher powers of current key
        for exp in range(2, 6):
            result = pow(current_key, exp)
            if result == target_key:
                formulas_to_test.append(f"k^{exp}")
                
            result = current_key + pow(current_key, exp)
            if result == target_key:
                formulas_to_test.append(f"k + k^{exp}")
        
        # Fibonacci-like patterns (using previous keys)
        if pos >= 3:
            prev_prev_key = verified_keys.get(pos-2, 0)
            result = current_key + prev_prev_key
            if result == target_key:
                formulas_to_test.append(f"k + k[pos-2]")
                
            result = current_key * 2 + prev_prev_key
            if result == target_key:
                formulas_to_test.append(f"2*k + k[pos-2]")
        
        # Complex bitwise operations
        for shift1 in range(1, 16):
            for shift2 in range(1, 16):
                if shift1 != shift2:
                    result = (current_key << shift1) + (current_key << shift2)
                    if result == target_key:
                        formulas_to_test.append(f"(k << {shift1}) + (k << {shift2})")
                        
                    result = (current_key << shift1) - (current_key << shift2)
                    if result == target_key:
                        formulas_to_test.append(f"(k << {shift1}) - (k << {shift2})")
        
        # Hash-like operations
        for mult in [31, 37, 41, 43, 47]:
            result = current_key * mult + pos
            if result == target_key:
                formulas_to_test.append(f"k * {mult} + pos")
                
            result = (current_key * mult) ^ pos
            if result == target_key:
                formulas_to_test.append(f"(k * {mult}) XOR pos")
        
        # Report findings
        if formulas_to_test:
            print(f"✓ FOUND FORMULAS:")
            for formula in formulas_to_test[:5]:  # Show first 5 matches
                print(f"  {formula}")
            if len(formulas_to_test) > 5:
                print(f"  ... and {len(formulas_to_test)-5} more")
        else:
            print(f"✗ NO SIMPLE FORMULAS FOUND")
            
            # Show the actual difference for manual analysis
            diff = target_key - current_key
            print(f"  Needed difference: {diff:,}")
            
            # Analyze the difference itself
            print(f"  Difference analysis:")
            print(f"    As ratio of current key: {diff/current_key:.3f}")
            print(f"    As power of 2: ~2^{diff.bit_length()-1}")
            print(f"    Binary: {bin(diff)}")
            
            # Check if it's close to powers of 2
            for exp in range(20, 70):
                power_of_2 = 1 << exp
                if abs(diff - power_of_2) < power_of_2 * 0.1:  # Within 10%
                    print(f"    Close to 2^{exp}: {power_of_2:,} (diff: {abs(diff-power_of_2):,})")
    
    print(f"\n=== ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    analyze_complex_patterns() 