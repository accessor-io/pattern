#!/usr/bin/env python3
"""Test and analyze the growing bitshift formulas from positions 15-17"""

def analyze_growing_formulas():
    """Analyze the pattern in the growing bitshift formulas"""
    
    # Known keys and their formulas
    test_cases = [
        {
            'pos': 15,
            'prev_key': 0x2930,
            'target_key': 0x68f3,
            'formula': 'k + (1<<14)-(1<<6)+(1<<1)+1',
            'description': 'k + 2^14 - 2^6 + 2^1 + 1'
        },
        {
            'pos': 16, 
            'prev_key': 0x68f3,
            'target_key': 0xc936,
            'formula': 'k + (1<<14)+(1<<13)+(1<<6)+(1<<1)+1',
            'description': 'k + 2^14 + 2^13 + 2^6 + 2^1 + 1'
        },
        {
            'pos': 17,
            'prev_key': 0xc936,
            'target_key': 0x1764f,
            'formula': 'k + (1<<15)+(1<<13)+(1<<11)+(1<<10)+(1<<8)+(1<<4)+(1<<3)+1',
            'description': 'k + 2^15 + 2^13 + 2^11 + 2^10 + 2^8 + 2^4 + 2^3 + 1'
        }
    ]
    
    print("=== GROWING BITSHIFT FORMULA ANALYSIS ===\n")
    
    for case in test_cases:
        print(f"Position {case['pos']}:")
        print(f"  Formula: {case['formula']}")
        print(f"  Description: {case['description']}")
        print(f"  Prev key: 0x{case['prev_key']:x}")
        print(f"  Target: 0x{case['target_key']:x}")
        
        # Test the formula
        if case['pos'] == 15:
            result = case['prev_key'] + (1<<14) - (1<<6) + (1<<1) + 1
        elif case['pos'] == 16:
            result = case['prev_key'] + (1<<14) + (1<<13) + (1<<6) + (1<<1) + 1
        elif case['pos'] == 17:
            result = case['prev_key'] + (1<<15) + (1<<13) + (1<<11) + (1<<10) + (1<<8) + (1<<4) + (1<<3) + 1
        
        print(f"  Calculated: 0x{result:x}")
        print(f"  Match: {'✓' if result == case['target_key'] else '✗'}")
        print()
    
    # Analyze the bit patterns
    print("=== BIT PATTERN ANALYSIS ===\n")
    
    formulas_bits = [
        # Position 15: (1<<14) - (1<<6) + (1<<1) + 1
        [14, -6, 1, 0],  # Using negative for subtraction, 0 for +1
        
        # Position 16: (1<<14) + (1<<13) + (1<<6) + (1<<1) + 1  
        [14, 13, 6, 1, 0],
        
        # Position 17: (1<<15) + (1<<13) + (1<<11) + (1<<10) + (1<<8) + (1<<4) + (1<<3) + 1
        [15, 13, 11, 10, 8, 4, 3, 0]
    ]
    
    for i, bits in enumerate(formulas_bits, 15):
        print(f"Position {i} bit powers: {bits}")
        
        # Calculate the actual constant being added
        constant = 0
        for bit in bits:
            if bit == 0:
                constant += 1  # The +1 term
            elif bit > 0:
                constant += (1 << bit)
            else:  # negative (subtraction)
                constant -= (1 << abs(bit))
        
        print(f"  Constant being added: {constant} (0x{constant:x})")
        print()
    
    # Look for patterns in the bit positions
    print("=== PATTERN ANALYSIS ===\n")
    
    print("Highest bit used:")
    print("  Position 15: 2^14")
    print("  Position 16: 2^14") 
    print("  Position 17: 2^15")
    print("  Pattern: Highest bit increases gradually")
    
    print("\nNumber of terms:")
    print("  Position 15: 4 terms (14, -6, 1, +1)")
    print("  Position 16: 5 terms (14, 13, 6, 1, +1)")
    print("  Position 17: 8 terms (15, 13, 11, 10, 8, 4, 3, +1)")
    print("  Pattern: Complexity increasing rapidly")
    
    print("\nCommon elements:")
    print("  All have: +1 at the end")
    print("  Positions 16-17 both have: 2^13")
    print("  Positions 15-16 both have: 2^6, 2^1")
    
    # Try to predict position 18
    print("\n=== POSITION 18 PREDICTION ===\n")
    
    # Based on the pattern, position 18 might use 2^16 as highest bit
    # and continue the complexity growth
    print("Predicted characteristics for position 18:")
    print("  - Highest bit: likely 2^16 or 2^17")
    print("  - Number of terms: 8-12 (continuing growth)")
    print("  - Will likely include 2^13 (appears in 16-17)")
    print("  - Will end with +1 (consistent pattern)")
    
    # Test some candidate patterns for position 18
    pos_17_key = 0x1764f
    print(f"\nIf we had position 18 target, we could test patterns like:")
    print(f"  Base key (pos 17): 0x{pos_17_key:x}")
    
    candidate_patterns = [
        # Pattern 1: Continue with 2^16
        (1<<16) + (1<<15) + (1<<13) + (1<<11) + (1<<9) + (1<<6) + (1<<3) + 1,
        # Pattern 2: Use 2^17 
        (1<<17) + (1<<14) + (1<<12) + (1<<10) + (1<<8) + (1<<5) + (1<<2) + 1,
        # Pattern 3: More complex combination
        (1<<16) + (1<<14) + (1<<13) + (1<<11) + (1<<10) + (1<<8) + (1<<6) + (1<<4) + 1
    ]
    
    for i, pattern in enumerate(candidate_patterns, 1):
        result = pos_17_key + pattern
        print(f"  Candidate {i}: k + 0x{pattern:x} = 0x{result:x}")

if __name__ == "__main__":
    analyze_growing_formulas() 