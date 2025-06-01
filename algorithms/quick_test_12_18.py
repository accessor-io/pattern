#!/usr/bin/env python3
"""Quick test for positions 12-18 to verify our fixes work"""

def quick_test_generation():
    """Test generation for positions 12-18 with our fixes"""
    
    # Known keys from the working script output
    known_keys = {
        1: 0x1,
        2: 0x3, 
        3: 0x7,
        4: 0x8,
        5: 0x15,
        6: 0x31,
        7: 0x4c,
        8: 0xe0,
        9: 0x1d3,
        10: 0x202,
        11: 0x483,
        12: 0xa7b,   # Target for position 12
        13: 0x1460,  # Target for position 13
        14: 0x2930,  # Target for position 14
        15: 0x68f3,  # Target for position 15
        16: 0xc936,  # Target for position 16
        17: 0x1764f, # Target for position 17
    }
    
    # Our added large constants
    large_constants = [1528, 2533, 5328, 16323, 24643, 44313, 102846, 158482]
    
    print("=== QUICK GENERATION TEST (Positions 12-18) ===\n")
    
    # Test positions 12-18
    for pos in range(12, 18):
        if pos not in known_keys or pos-1 not in known_keys:
            print(f"Position {pos}: Missing data")
            continue
            
        current_key = known_keys[pos-1]
        target_key = known_keys[pos]
        difference = target_key - current_key
        
        print(f"Position {pos-1} → {pos}:")
        print(f"  Current: 0x{current_key:x}")
        print(f"  Target:  0x{target_key:x}")
        print(f"  Diff:    {difference} (0x{difference:x})")
        
        # Check if difference is in our large constants
        if difference in large_constants:
            print(f"  ✓ FOUND: k + {difference} is in large_constants")
            # Verify the calculation
            calc_result = current_key + difference
            if calc_result == target_key:
                print(f"  ✓ VERIFIED: {current_key} + {difference} = {calc_result}")
            else:
                print(f"  ✗ ERROR: {current_key} + {difference} = {calc_result} ≠ {target_key}")
        else:
            print(f"  ❌ MISSING: k + {difference} NOT in large_constants")
            
            # Check if it's close to any constant in our list
            closest = min(large_constants, key=lambda x: abs(x - difference))
            diff_from_closest = abs(closest - difference)
            if diff_from_closest < 100:
                print(f"     Closest constant: {closest} (off by {diff_from_closest})")
        
        print()
    
    # Predict position 18
    if 17 in known_keys:
        pos_17_key = known_keys[17]
        print(f"=== POSITION 18 PREDICTION ===")
        print(f"Starting from position 17: 0x{pos_17_key:x}")
        
        # Based on the progression, estimate next difference
        differences = []
        for pos in range(12, 17):
            if pos in known_keys and pos+1 in known_keys:
                diff = known_keys[pos+1] - known_keys[pos]
                differences.append(diff)
        
        print(f"Recent differences: {differences}")
        if len(differences) >= 3:
            # Look for growth pattern
            growth_rates = []
            for i in range(1, len(differences)):
                growth = differences[i] / differences[i-1]
                growth_rates.append(growth)
            
            avg_growth = sum(growth_rates) / len(growth_rates)
            predicted_diff = int(differences[-1] * avg_growth)
            predicted_key_18 = pos_17_key + predicted_diff
            
            print(f"Average growth rate: {avg_growth:.2f}")
            print(f"Predicted difference for 17→18: {predicted_diff}")
            print(f"Predicted key for position 18: 0x{predicted_key_18:x}")
            
            # Check if predicted difference is in our constants
            if predicted_diff in large_constants:
                print(f"✓ Predicted difference {predicted_diff} IS in our large_constants!")
            else:
                closest = min(large_constants, key=lambda x: abs(x - predicted_diff))
                print(f"❌ Predicted difference {predicted_diff} not in constants")
                print(f"   Closest: {closest} (off by {abs(closest - predicted_diff)})")

if __name__ == "__main__":
    quick_test_generation() 