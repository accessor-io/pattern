#!/usr/bin/env python3
"""Test bitshift patterns for positions 30-68 based on powers of 2 analysis"""

def test_bitshift_patterns():
    """Test bitshift operations for positions 30-68"""
    
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
    
    print(f"\n=== TESTING BITSHIFT PATTERNS (Positions 30-68) ===")
    print(f"Based on observation: differences are close to powers of 2")
    
    successful_formulas = {}
    failed_positions = []
    
    for pos in range(30, min(69, max(verified_keys.keys()) + 1)):
        if pos not in verified_keys or pos-1 not in verified_keys:
            continue
            
        current_key = verified_keys[pos-1]
        target_key = verified_keys[pos]
        needed_diff = target_key - current_key
        
        print(f"\n--- Position {pos-1} → {pos} ---")
        print(f"Needed: {needed_diff:,}")
        
        found_formulas = []
        
        # Test bitshift operations
        for shift in range(20, 70):  # Focus on larger shifts based on analysis
            power_of_2 = 1 << shift
            
            # Test exact power of 2 addition
            if current_key + power_of_2 == target_key:
                found_formulas.append(f"k + (1 << {shift})")
                print(f"  ✓ EXACT: k + (1 << {shift}) = k + 2^{shift}")
            
            # Test power of 2 with small adjustments
            for adj in range(-1000, 1001, 100):  # Test small adjustments
                if current_key + power_of_2 + adj == target_key:
                    if adj == 0:
                        found_formulas.append(f"k + (1 << {shift})")
                        print(f"  ✓ EXACT: k + (1 << {shift})")
                    elif adj > 0:
                        found_formulas.append(f"k + (1 << {shift}) + {adj}")
                        print(f"  ✓ CLOSE: k + (1 << {shift}) + {adj}")
                    else:
                        found_formulas.append(f"k + (1 << {shift}) - {abs(adj)}")
                        print(f"  ✓ CLOSE: k + (1 << {shift}) - {abs(adj)}")
            
            # Test multiple bitshifts combined
            for shift2 in range(shift+1, min(shift+10, 70)):
                if current_key + power_of_2 + (1 << shift2) == target_key:
                    found_formulas.append(f"k + (1 << {shift}) + (1 << {shift2})")
                    print(f"  ✓ MULTI: k + (1 << {shift}) + (1 << {shift2})")
                    
                if current_key + power_of_2 - (1 << shift2) == target_key:
                    found_formulas.append(f"k + (1 << {shift}) - (1 << {shift2})")
                    print(f"  ✓ MULTI: k + (1 << {shift}) - (1 << {shift2})")
        
        # Test k << shift operations (multiplication by powers of 2)
        for shift in range(1, 20):
            if (current_key << shift) == target_key:
                found_formulas.append(f"k << {shift}")
                print(f"  ✓ SHIFT: k << {shift} (multiply by 2^{shift})")
            
            # Test k << shift with additions
            for add_shift in range(1, 10):
                if ((current_key << shift) + (1 << add_shift)) == target_key:
                    found_formulas.append(f"(k << {shift}) + (1 << {add_shift})")
                    print(f"  ✓ SHIFT+: (k << {shift}) + (1 << {add_shift})")
        
        # Test position-dependent bitshift patterns
        for base_shift in range(20, 35):
            # Position-modulated shifts
            shift_amount = base_shift + (pos % 5)
            if current_key + (1 << shift_amount) == target_key:
                found_formulas.append(f"k + (1 << ({base_shift} + pos%5))")
                print(f"  ✓ POS: k + (1 << {shift_amount}) [base:{base_shift} + pos%5]")
        
        # Test Fibonacci-like bitshift patterns
        if pos >= 32:  # Need enough history
            # Get previous differences to see if there's a pattern
            prev_diffs = []
            for i in range(max(30, pos-5), pos):
                if i in verified_keys and i-1 in verified_keys:
                    prev_diffs.append(verified_keys[i] - verified_keys[i-1])
            
            if len(prev_diffs) >= 2:
                # Test if current difference is sum of previous
                if needed_diff == prev_diffs[-1] + prev_diffs[-2]:
                    found_formulas.append("Fibonacci-like: diff = prev_diff + prev_prev_diff")
                    print(f"  ✓ FIBO: Current diff = sum of last 2 diffs")
        
        if found_formulas:
            successful_formulas[pos] = found_formulas
            print(f"  ✓ FOUND {len(found_formulas)} FORMULA(S)")
        else:
            failed_positions.append(pos)
            print(f"  ✗ NO FORMULAS FOUND")
            
            # Show closest powers of 2 for analysis
            closest_powers = []
            for shift in range(20, 70):
                power_of_2 = 1 << shift
                diff = abs(needed_diff - power_of_2)
                closest_powers.append((shift, power_of_2, diff))
            
            # Sort by difference and show top 3
            closest_powers.sort(key=lambda x: x[2])
            print(f"    Closest powers of 2:")
            for shift, power, diff in closest_powers[:3]:
                percentage = (diff / needed_diff) * 100
                print(f"      2^{shift}: {power:,} (off by {diff:,}, {percentage:.1f}%)")
    
    # Summary
    print(f"\n=== BITSHIFT PATTERN SUMMARY ===")
    total_tested = len([p for p in range(30, min(69, max(verified_keys.keys()) + 1)) 
                       if p in verified_keys and p-1 in verified_keys])
    successful_count = len(successful_formulas)
    success_rate = (successful_count / total_tested * 100) if total_tested > 0 else 0
    
    print(f"Positions tested: {total_tested}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(failed_positions)}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if successful_formulas:
        print(f"\n--- Successful Bitshift Formulas ---")
        for pos, formulas in successful_formulas.items():
            print(f"  Position {pos}: {formulas[0]}")  # Show first formula
    
    if failed_positions and len(failed_positions) <= 10:
        print(f"\n--- Failed Positions ---")
        for pos in failed_positions:
            if pos in verified_keys and pos-1 in verified_keys:
                diff = verified_keys[pos] - verified_keys[pos-1]
                print(f"  Position {pos}: needs {diff:,}")

if __name__ == "__main__":
    test_bitshift_patterns() 