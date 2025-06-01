#!/usr/bin/env python3
"""Analyze the extended Bitcoin puzzle sequence with newly provided values"""

def analyze_extended_sequence():
    """Analyze the newly provided Bitcoin puzzle private keys for positions 66-130"""
    
    print("🔍 ANALYZING EXTENDED BITCOIN PUZZLE SEQUENCE (66-130)")
    print("=" * 80)
    
    # Newly provided verified private keys
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
    
    print(f"✓ Loaded {len(extended_keys)} extended private keys")
    print()
    
    # Analyze differences between consecutive known positions
    print("--- DIFFERENCES BETWEEN CONSECUTIVE POSITIONS ---")
    sorted_positions = sorted(extended_keys.keys())
    
    consecutive_pairs = []
    for i in range(len(sorted_positions) - 1):
        pos1 = sorted_positions[i]
        pos2 = sorted_positions[i + 1]
        if pos2 == pos1 + 1:  # Only consecutive positions
            consecutive_pairs.append((pos1, pos2))
    
    print("Consecutive position pairs found:")
    for pos1, pos2 in consecutive_pairs:
        key1 = extended_keys[pos1]
        key2 = extended_keys[pos2]
        diff = key2 - key1
        print(f"Position {pos1} → {pos2}: {diff:,} (0x{diff:x})")
    
    # Analyze the critical transition 68→69
    print(f"\n--- CRITICAL TRANSITION ANALYSIS: 68→69 ---")
    if 68 in extended_keys and 69 in extended_keys:
        key_68 = extended_keys[68]
        key_69 = extended_keys[69]
        diff_68_69 = key_69 - key_68
        
        print(f"Position 68: 0x{key_68:x}")
        print(f"Position 69: 0x{key_69:x}")
        print(f"Difference:  {diff_68_69:,} (0x{diff_68_69:x})")
        
        # Compare with our previous analysis of 67→68
        if 67 in extended_keys:
            key_67 = extended_keys[67]
            diff_67_68 = key_68 - key_67
            ratio_68_69 = diff_68_69 / diff_67_68 if diff_67_68 > 0 else 0
            
            print(f"\nComparison with previous transition:")
            print(f"67→68 difference: {diff_67_68:,}")
            print(f"68→69 difference: {diff_68_69:,}")
            print(f"Growth ratio: {ratio_68_69:.3f}")
            
            # Test if our growth pattern prediction was close
            if ratio_68_69 > 50:  # Massive jump
                print(f"🚨 MASSIVE JUMP DETECTED! Ratio = {ratio_68_69:.1f}x")
                print(f"   This confirms our theory that position 69+ uses different generation!")
            else:
                print(f"📊 Moderate growth - pattern may continue")
    
    # Analyze gaps and jumps in non-consecutive positions
    print(f"\n--- GAP ANALYSIS (NON-CONSECUTIVE POSITIONS) ---")
    gap_analysis = []
    for i in range(len(sorted_positions) - 1):
        pos1 = sorted_positions[i]
        pos2 = sorted_positions[i + 1]
        if pos2 > pos1 + 1:  # Gap exists
            gap_size = pos2 - pos1
            key1 = extended_keys[pos1]
            key2 = extended_keys[pos2]
            diff = key2 - key1
            diff_per_position = diff / gap_size
            gap_analysis.append((pos1, pos2, gap_size, diff, diff_per_position))
    
    for pos1, pos2, gap_size, total_diff, avg_diff in gap_analysis:
        print(f"Gap {pos1}→{pos2} ({gap_size} positions):")
        print(f"  Total difference: {total_diff:,}")
        print(f"  Average per position: {avg_diff:,.0f}")
        print()
    
    # Check for powers of 2 patterns in the ranges
    print(f"--- POWERS OF 2 ANALYSIS ---")
    for pos in sorted_positions:
        key = extended_keys[pos]
        # Find the closest power of 2
        bit_length = key.bit_length()
        lower_power = 1 << (bit_length - 1)
        upper_power = 1 << bit_length
        
        lower_diff = key - lower_power
        upper_diff = upper_power - key
        
        if lower_diff < upper_diff:
            closest_power = lower_power
            closest_power_exp = bit_length - 1
            diff_from_power = lower_diff
        else:
            closest_power = upper_power
            closest_power_exp = bit_length
            diff_from_power = -upper_diff
        
        ratio_to_power = abs(diff_from_power) / closest_power * 100
        
        print(f"Position {pos:3}: 0x{key:x}")
        print(f"          Closest to 2^{closest_power_exp} = {closest_power:,}")
        print(f"          Difference: {diff_from_power:+,} ({ratio_to_power:.1f}% of 2^{closest_power_exp})")
        print()
    
    # Check if keys are within their expected bit ranges
    print(f"--- BIT RANGE VALIDATION ---")
    for pos in sorted_positions:
        key = extended_keys[pos]
        expected_min = 1 << (pos - 1)
        expected_max = (1 << pos) - 1
        
        in_range = expected_min <= key <= expected_max
        bit_position = key.bit_length()
        
        print(f"Position {pos:3}: Expected {pos}-bit range, actual {bit_position}-bit")
        print(f"          Key: 0x{key:x}")
        print(f"          Range: 0x{expected_min:x} to 0x{expected_max:x}")
        print(f"          Valid: {'✓' if in_range else '✗'}")
        
        if not in_range:
            if key < expected_min:
                print(f"          ERROR: Key too small by {expected_min - key:,}")
            else:
                print(f"          ERROR: Key too large by {key - expected_max:,}")
        print()
    
    # Statistical analysis of the extended sequence
    print(f"--- STATISTICAL ANALYSIS ---")
    
    # Growth analysis between available positions
    growth_ratios = []
    for i in range(len(sorted_positions) - 1):
        pos1 = sorted_positions[i]
        pos2 = sorted_positions[i + 1]
        key1 = extended_keys[pos1]
        key2 = extended_keys[pos2]
        
        if key1 > 0:
            ratio = key2 / key1
            growth_ratios.append((f"{pos1}→{pos2}", ratio))
    
    print("Growth ratios between available positions:")
    for transition, ratio in growth_ratios:
        print(f"  {transition:6}: {ratio:8.2f}x")
    
    # Check for randomness vs patterns in higher positions
    print(f"\n--- RANDOMNESS ANALYSIS ---")
    
    # For positions 69+, check if they follow any mathematical relationship
    high_positions = [pos for pos in sorted_positions if pos >= 69]
    if len(high_positions) >= 2:
        print("Testing for patterns in positions 69+:")
        
        for i in range(len(high_positions) - 1):
            pos1 = high_positions[i]
            pos2 = high_positions[i + 1]
            key1 = extended_keys[pos1]
            key2 = extended_keys[pos2]
            
            # Test simple relationships
            if pos2 == pos1 + 1:  # Only for consecutive positions
                diff = key2 - key1
                ratio = key2 / key1 if key1 > 0 else 0
                
                print(f"  {pos1}→{pos2}: diff = {diff:,}, ratio = {ratio:.3f}")
                
                # Check if difference follows any power pattern
                bit_length = diff.bit_length()
                closest_power_2 = 1 << (bit_length - 1)
                power_diff = abs(diff - closest_power_2)
                power_ratio = power_diff / closest_power_2 * 100
                
                if power_ratio < 10:  # Within 10% of a power of 2
                    print(f"    Close to 2^{bit_length-1}: {power_ratio:.1f}% difference")
    
    return extended_keys

def compare_with_original_analysis():
    """Compare the new data with our original analysis"""
    
    print(f"\n--- COMPARISON WITH ORIGINAL ANALYSIS ---")
    
    # Load our original verified sequence
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
        print("Could not load original sequence")
        return
    
    # Compare overlapping positions
    extended_keys = analyze_extended_sequence()
    
    overlapping_positions = set(original_keys.keys()) & set(extended_keys.keys())
    
    print(f"Overlapping positions to verify: {sorted(overlapping_positions)}")
    
    all_match = True
    for pos in sorted(overlapping_positions):
        original = original_keys[pos]
        extended = extended_keys[pos]
        match = original == extended
        all_match = all_match and match
        
        print(f"Position {pos}: {'✓' if match else '✗'}")
        if not match:
            print(f"  Original:  0x{original:x}")
            print(f"  Extended:  0x{extended:x}")
            print(f"  Difference: {abs(original - extended):,}")
    
    if all_match:
        print(f"🎉 ALL OVERLAPPING POSITIONS MATCH! Data is consistent!")
    else:
        print(f"❌ Some positions don't match - need to verify data")
    
    return all_match

if __name__ == "__main__":
    analyze_extended_sequence()
    compare_with_original_analysis() 