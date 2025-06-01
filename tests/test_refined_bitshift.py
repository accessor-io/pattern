#!/usr/bin/env python3
"""Test refined bitshift patterns: k + 2^n ± adjustment"""

def test_refined_bitshift_patterns():
    """Test patterns of the form k + 2^n ± small_adjustment"""
    
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
    
    print(f"\n=== TESTING REFINED BITSHIFT PATTERNS ===")
    print(f"Testing: k + 2^n ± adjustment (larger adjustment range)")
    
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
        
        # Test k + 2^n ± adjustment with much larger adjustment range
        for shift in range(20, 70):
            power_of_2 = 1 << shift
            
            # Calculate the adjustment needed
            adjustment = needed_diff - power_of_2
            
            # Test if this adjustment is "reasonable" (not too large compared to the power of 2)
            if abs(adjustment) < power_of_2 * 0.5:  # Within 50% of the power of 2
                percentage = abs(adjustment) / needed_diff * 100
                
                if adjustment == 0:
                    found_formulas.append(f"k + 2^{shift}")
                    print(f"  ✓ EXACT: k + 2^{shift}")
                elif adjustment > 0:
                    found_formulas.append(f"k + 2^{shift} + {adjustment:,}")
                    print(f"  ✓ CLOSE: k + 2^{shift} + {adjustment:,} (off by {percentage:.1f}%)")
                else:
                    found_formulas.append(f"k + 2^{shift} - {abs(adjustment):,}")
                    print(f"  ✓ CLOSE: k + 2^{shift} - {abs(adjustment):,} (off by {percentage:.1f}%)")
        
        # Test more complex combinations
        for shift1 in range(20, 60):
            power1 = 1 << shift1
            
            # Test 2^shift1 + 2^shift2 combinations
            for shift2 in range(shift1+1, min(shift1+15, 70)):
                power2 = 1 << shift2
                combined = power1 + power2
                adjustment = needed_diff - combined
                
                if abs(adjustment) < combined * 0.3:  # Within 30%
                    if adjustment == 0:
                        found_formulas.append(f"k + 2^{shift1} + 2^{shift2}")
                        print(f"  ✓ MULTI: k + 2^{shift1} + 2^{shift2}")
                    elif abs(adjustment) < combined * 0.1:  # Very close
                        if adjustment > 0:
                            found_formulas.append(f"k + 2^{shift1} + 2^{shift2} + {adjustment:,}")
                            print(f"  ✓ MULTI+: k + 2^{shift1} + 2^{shift2} + {adjustment:,}")
                        else:
                            found_formulas.append(f"k + 2^{shift1} + 2^{shift2} - {abs(adjustment):,}")
                            print(f"  ✓ MULTI-: k + 2^{shift1} + 2^{shift2} - {abs(adjustment):,}")
            
            # Test 2^shift1 - 2^shift2 combinations
            for shift2 in range(shift1-10, shift1):
                if shift2 > 0:
                    power2 = 1 << shift2
                    combined = power1 - power2
                    adjustment = needed_diff - combined
                    
                    if abs(adjustment) < combined * 0.3:  # Within 30%
                        if adjustment == 0:
                            found_formulas.append(f"k + 2^{shift1} - 2^{shift2}")
                            print(f"  ✓ DIFF: k + 2^{shift1} - 2^{shift2}")
                        elif abs(adjustment) < combined * 0.1:  # Very close
                            if adjustment > 0:
                                found_formulas.append(f"k + 2^{shift1} - 2^{shift2} + {adjustment:,}")
                                print(f"  ✓ DIFF+: k + 2^{shift1} - 2^{shift2} + {adjustment:,}")
                            else:
                                found_formulas.append(f"k + 2^{shift1} - 2^{shift2} - {abs(adjustment):,}")
                                print(f"  ✓ DIFF-: k + 2^{shift1} - 2^{shift2} - {abs(adjustment):,}")
        
        # Test position-dependent power adjustments
        for base_shift in range(25, 45):
            # Position-modulated shifts
            shift_amount = base_shift + (pos % 8)
            power_of_2 = 1 << shift_amount
            adjustment = needed_diff - power_of_2
            
            if abs(adjustment) < power_of_2 * 0.2:  # Within 20%
                if adjustment == 0:
                    found_formulas.append(f"k + 2^({base_shift} + pos%8)")
                    print(f"  ✓ POS: k + 2^{shift_amount} [base:{base_shift} + pos%8]")
                elif abs(adjustment) < power_of_2 * 0.05:  # Very close
                    percentage = abs(adjustment) / needed_diff * 100
                    if adjustment > 0:
                        found_formulas.append(f"k + 2^({base_shift} + pos%8) + {adjustment:,}")
                        print(f"  ✓ POS+: k + 2^{shift_amount} + {adjustment:,} [off by {percentage:.1f}%]")
                    else:
                        found_formulas.append(f"k + 2^({base_shift} + pos%8) - {abs(adjustment):,}")
                        print(f"  ✓ POS-: k + 2^{shift_amount} - {abs(adjustment):,} [off by {percentage:.1f}%]")
        
        if found_formulas:
            successful_formulas[pos] = found_formulas
            print(f"  ✓ FOUND {len(found_formulas)} FORMULA(S)")
        else:
            failed_positions.append(pos)
            print(f"  ✗ NO FORMULAS FOUND")
            
            # Show the best approximation for failed cases
            best_shift = None
            best_adjustment = None
            best_percentage = float('inf')
            
            for shift in range(20, 70):
                power_of_2 = 1 << shift
                adjustment = needed_diff - power_of_2
                percentage = abs(adjustment) / needed_diff * 100
                
                if percentage < best_percentage:
                    best_percentage = percentage
                    best_shift = shift
                    best_adjustment = adjustment
            
            if best_shift is not None:
                if best_adjustment > 0:
                    print(f"  Best: k + 2^{best_shift} + {best_adjustment:,} (off by {best_percentage:.1f}%)")
                else:
                    print(f"  Best: k + 2^{best_shift} - {abs(best_adjustment):,} (off by {best_percentage:.1f}%)")
    
    # Summary
    print(f"\n=== REFINED BITSHIFT SUMMARY ===")
    total_tested = len([p for p in range(30, min(69, max(verified_keys.keys()) + 1)) 
                       if p in verified_keys and p-1 in verified_keys])
    successful_count = len(successful_formulas)
    success_rate = (successful_count / total_tested * 100) if total_tested > 0 else 0
    
    print(f"Positions tested: {total_tested}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(failed_positions)}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if successful_formulas:
        print(f"\n--- Successful Refined Formulas ---")
        for pos, formulas in successful_formulas.items():
            print(f"  Position {pos}: {formulas[0]}")  # Show first formula

if __name__ == "__main__":
    test_refined_bitshift_patterns() 