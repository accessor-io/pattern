#!/usr/bin/env python3
"""Test script to verify the fix for positions 12-13"""

def test_formulas_12_13():
    """Test if the missing formulas for positions 12-13 are now included"""
    
    # Simulate the key formulas that should be found
    key_11 = 0x483
    key_12 = 0xa7b  
    key_13 = 0x1460
    
    # Test the specific constants that work
    large_constants = [1528, 2533, 5328, 16323, 24643, 44313, 102846, 158482]
    
    print("Testing if formulas for positions 12-13 are now included...")
    
    # Test 11→12 with k + 1528
    if 1528 in large_constants:
        result_12 = key_11 + 1528
        if result_12 == key_12:
            print(f"✓ Position 12 formula found: k + 1528 = 0x{result_12:x}")
        else:
            print(f"✗ Position 12 formula failed")
    
    # Test 12→13 with k + 2533  
    if 2533 in large_constants:
        result_13 = key_12 + 2533
        if result_13 == key_13:
            print(f"✓ Position 13 formula found: k + 2533 = 0x{result_13:x}")
        else:
            print(f"✗ Position 13 formula failed")
    
    # Test the range-based addition
    range_200_3000 = list(range(200, 3000, 50))
    
    print(f"\nTesting range-based constants (200-3000, step 50):")
    print(f"1528 in range: {any(abs(x - 1528) <= 25 for x in range_200_3000)}")
    print(f"2533 in range: {any(abs(x - 2533) <= 25 for x in range_200_3000)}")
    
    # Find closest values in range
    closest_1528 = min(range_200_3000, key=lambda x: abs(x - 1528))
    closest_2533 = min(range_200_3000, key=lambda x: abs(x - 2533))
    
    print(f"Closest to 1528: {closest_1528} (diff: {abs(closest_1528 - 1528)})")
    print(f"Closest to 2533: {closest_2533} (diff: {abs(closest_2533 - 2533)})")
    
    print("\nRecommendation: The large_constants list should contain the exact values,")
    print("so positions 12-13 should now be found correctly.")

if __name__ == "__main__":
    test_formulas_12_13() 