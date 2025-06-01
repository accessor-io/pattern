#!/usr/bin/env python3
"""Discover the extended algorithmic pattern for Bitcoin puzzles positions 66-130"""

import math

def discover_extended_pattern():
    """Discover the extended pattern using the new data"""
    
    print("🔍 DISCOVERING EXTENDED BITCOIN PUZZLE PATTERN")
    print("=" * 70)
    
    # Complete extended dataset (combining original + new data)
    extended_keys = {
        66: 0x2832ed74f2b5e35ee,
        67: 0x730fc235c1942c1ae,
        68: 0xbebb3940cd0fc1491,
        69: 0x101d83275fb2bc7e0c,
        70: 0x349b84b6431a6c4ef1,
        75: 0x4c5ce114686a1336e07,
        80: 0xea1a5c66dcc1b5ad180,
        85: 0x1f720c4f018d51b8cebba8,
        90: 0x2ce00bb2136a445c71e85bf,
        95: 0x527a792b183c7f64a0e8b1f4,
        100: 0xaf55fc59c335c8ec67ed24826,
        105: 0x16f14fc2054cd87ee6396b33df3,
        110: 0x35c0d7234df7deb0f20cf7062444,
        115: 0x60f4d11574f5deee49961d9609ac6,
        120: 0xb10f22572c497a836ea187f2e1fc23,
        125: 0x1c533b6bb7f0804e09960225e44877ac,
        130: 0x33e766570535904f28b88cf897c603c9,
    }
    
    print(f"✓ Analyzing {len(extended_keys)} positions for extended pattern")
    print()
    
    # Test the extended pattern hypothesis: key[n] ≈ 2^(n-1) + adjustment
    print("--- TESTING EXTENDED PATTERN: key[n] = 2^(n-1) + adjustment ---")
    
    pattern_results = {}
    
    for pos in sorted(extended_keys.keys()):
        key = extended_keys[pos]
        
        # Test different base powers
        patterns_tested = []
        
        # Test 2^(n-1) - traditional puzzle pattern
        base_power_n_minus_1 = 1 << (pos - 1)
        adjustment_n_minus_1 = key - base_power_n_minus_1
        ratio_n_minus_1 = abs(adjustment_n_minus_1) / base_power_n_minus_1 * 100
        patterns_tested.append(('2^(n-1)', base_power_n_minus_1, adjustment_n_minus_1, ratio_n_minus_1))
        
        # Test 2^n
        base_power_n = 1 << pos
        adjustment_n = key - base_power_n
        ratio_n = abs(adjustment_n) / base_power_n * 100
        patterns_tested.append(('2^n', base_power_n, adjustment_n, ratio_n))
        
        # Test 2^(n-2)
        if pos >= 2:
            base_power_n_minus_2 = 1 << (pos - 2)
            adjustment_n_minus_2 = key - base_power_n_minus_2
            ratio_n_minus_2 = abs(adjustment_n_minus_2) / base_power_n_minus_2 * 100
            patterns_tested.append(('2^(n-2)', base_power_n_minus_2, adjustment_n_minus_2, ratio_n_minus_2))
        
        # Find the best fitting pattern (lowest ratio)
        best_pattern = min(patterns_tested, key=lambda x: x[3])
        pattern_type, base_power, adjustment, ratio = best_pattern
        
        pattern_results[pos] = {
            'key': key,
            'pattern_type': pattern_type,
            'base_power': base_power,
            'adjustment': adjustment,
            'ratio': ratio
        }
        
        print(f"Position {pos:3}: 0x{key:x}")
        print(f"          Best fit: {pattern_type}")
        print(f"          Base: {base_power:,}")
        print(f"          Adjustment: {adjustment:+,} ({ratio:.1f}%)")
        print()
    
    # Analyze patterns in adjustments
    print("--- ADJUSTMENT PATTERN ANALYSIS ---")
    
    # Group by pattern type
    pattern_groups = {}
    for pos, result in pattern_results.items():
        pattern_type = result['pattern_type']
        if pattern_type not in pattern_groups:
            pattern_groups[pattern_type] = []
        pattern_groups[pattern_type].append((pos, result))
    
    for pattern_type, positions in pattern_groups.items():
        print(f"\n{pattern_type} pattern positions: {[pos for pos, _ in positions]}")
        
        adjustments = [result['adjustment'] for pos, result in positions]
        ratios = [result['ratio'] for pos, result in positions]
        
        print(f"  Adjustment range: {min(adjustments):+,} to {max(adjustments):+,}")
        print(f"  Ratio range: {min(ratios):.1f}% to {max(ratios):.1f}%")
        print(f"  Average ratio: {sum(ratios)/len(ratios):.1f}%")
    
    # Test for predictive patterns in adjustments
    print("\n--- PREDICTIVE PATTERN ANALYSIS ---")
    
    # Look for patterns in adjustment sequences
    sorted_positions = sorted(extended_keys.keys())
    
    # Test if adjustments follow mathematical relationships
    print("Testing adjustment relationships:")
    
    for i, pos in enumerate(sorted_positions[:-1]):
        next_pos = sorted_positions[i + 1]
        
        if pos + 1 == next_pos:  # Only consecutive positions
            current_adj = pattern_results[pos]['adjustment']
            next_adj = pattern_results[next_pos]['adjustment']
            
            # Test various relationships
            if next_adj != 0 and current_adj != 0:
                ratio = next_adj / current_adj
                print(f"  {pos}→{next_pos}: adjustment ratio = {ratio:.3f}")
                
                # Test if close to powers of 2
                for power in range(-5, 6):
                    power_of_2 = 2 ** power
                    if abs(ratio - power_of_2) < power_of_2 * 0.1:  # Within 10%
                        print(f"    Close to 2^{power} = {power_of_2:.3f}")
    
    # Generate predictive formulas
    print("\n--- PREDICTIVE FORMULAS ---")
    
    # For each position, create a formula that could predict the key
    formulas = {}
    
    for pos in sorted_positions:
        result = pattern_results[pos]
        pattern_type = result['pattern_type']
        adjustment = result['adjustment']
        ratio = result['ratio']
        
        if pattern_type == '2^(n-1)':
            if ratio < 10:  # Very close to power of 2
                formulas[pos] = f"key[{pos}] ≈ 2^{pos-1} + {adjustment:+,}"
            else:
                formulas[pos] = f"key[{pos}] ≈ 2^{pos-1} + complex_adjustment"
        elif pattern_type == '2^n':
            if ratio < 10:
                formulas[pos] = f"key[{pos}] ≈ 2^{pos} + {adjustment:+,}"
            else:
                formulas[pos] = f"key[{pos}] ≈ 2^{pos} + complex_adjustment"
    
    for pos, formula in formulas.items():
        print(f"  {formula}")
    
    # Test if we can predict missing positions
    print("\n--- PREDICTION TESTING ---")
    
    # Test prediction for position 71-74 (between 70 and 75)
    if 70 in pattern_results and 75 in pattern_results:
        print("Attempting to predict positions 71-74:")
        
        key_70 = extended_keys[70]
        key_75 = extended_keys[75]
        
        # Linear interpolation as baseline
        for test_pos in range(71, 75):
            # Simple power-of-2 based prediction
            predicted_base = 1 << (test_pos - 1)
            
            # Estimate adjustment based on neighboring positions
            adj_70 = pattern_results[70]['adjustment']
            adj_75 = pattern_results[75]['adjustment']
            
            # Interpolate adjustment
            pos_ratio = (test_pos - 70) / (75 - 70)
            estimated_adj = adj_70 + (adj_75 - adj_70) * pos_ratio
            
            predicted_key = predicted_base + int(estimated_adj)
            
            print(f"  Position {test_pos}: predicted 0x{predicted_key:x}")
            print(f"    Base 2^{test_pos-1}: {predicted_base:,}")
            print(f"    Estimated adjustment: {int(estimated_adj):+,}")
    
    return pattern_results

def validate_extended_hypothesis():
    """Validate that the extended pattern explains all known positions"""
    
    print("\n🔬 VALIDATING EXTENDED PATTERN HYPOTHESIS")
    print("=" * 60)
    
    # Load original sequence data for validation
    original_keys = {}
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
                
                if pos <= 68 and 'KNOWN' in hex_and_status:
                    original_keys[pos] = int(hex_key, 16)
    except:
        print("Could not load original sequence - continuing with extended data only")
    
    # Test the hypothesis on a broader range
    test_positions = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70]
    
    print("Testing 2^(n-1) + adjustment pattern on positions 60-70:")
    
    for pos in test_positions:
        if pos in original_keys:
            key = original_keys[pos]
            source = "original"
        elif pos in [66, 67, 68, 69, 70]:  # From extended data
            extended_data = {
                66: 0x2832ed74f2b5e35ee,
                67: 0x730fc235c1942c1ae,
                68: 0xbebb3940cd0fc1491,
                69: 0x101d83275fb2bc7e0c,
                70: 0x349b84b6431a6c4ef1,
            }
            key = extended_data[pos]
            source = "extended"
        else:
            continue
        
        base_power = 1 << (pos - 1)
        adjustment = key - base_power
        ratio = abs(adjustment) / base_power * 100
        
        print(f"Position {pos} ({source}): ratio = {ratio:5.1f}%")
        
        if ratio < 15:  # Within 15% of power of 2
            print(f"  ✓ FITS PATTERN: 2^{pos-1} + {adjustment:+,}")
        else:
            print(f"  ? COMPLEX: 2^{pos-1} + {adjustment:+,}")

if __name__ == "__main__":
    pattern_results = discover_extended_pattern()
    validate_extended_hypothesis() 