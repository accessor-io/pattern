#!/usr/bin/env python3
"""Test script to verify the expanded constants are working"""

def test_expanded_constants():
    """Test the expanded large_constants list"""
    
    # Copy the expanded list from key_sequence_generator.py
    large_constants = [
        # Known working constants (positions 12-17)
        1528, 2533, 5328, 16323, 24643, 44313, 102846, 158482,
        
        # Predicted constants for position 18+ (based on ~2.12x growth pattern)
        93887, 94000, 95000, 96000, 97000, 98000, 99000, 100000, 101000, 102000, 103000, 104000, 105000,
        
        # Position 19+ predictions (exponential growth)
        200000, 210000, 220000, 230000, 240000, 250000, 260000, 270000, 280000, 290000, 300000,
        320000, 340000, 360000, 380000, 400000, 420000, 440000, 460000, 480000, 500000,
        
        # Position 22+ predictions (larger jumps)
        600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000,
        1600000, 1700000, 1800000, 1900000, 2000000, 2200000, 2400000, 2600000, 2800000, 3000000,
        
        # Position 25+ predictions (very large constants)
        3500000, 4000000, 4500000, 5000000, 5500000, 6000000, 6500000, 7000000, 7500000, 8000000,
        9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000, 16000000, 17000000, 18000000,
        20000000, 22000000, 24000000, 26000000, 28000000, 30000000, 32000000, 34000000, 36000000, 38000000,
        40000000, 45000000, 50000000, 55000000, 60000000, 65000000, 70000000, 75000000, 80000000, 85000000,
        90000000, 95000000, 100000000, 110000000, 120000000, 130000000, 140000000, 150000000,
        
        # Position 30+ predictions (extremely large constants)
        200000000, 250000000, 300000000, 350000000, 400000000, 450000000, 500000000,
        600000000, 700000000, 800000000, 900000000, 1000000000, 1200000000, 1400000000,
        1600000000, 1800000000, 2000000000, 2500000000, 3000000000,
        
        # Fill gaps around known constants with finer granularity
        1500, 1520, 1540, 1560, 1580, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000,
        2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000,
        5000, 5200, 5400, 5600, 5800, 6000, 6200, 6400, 6600, 6800, 7000,
        16000, 16500, 17000, 17500, 18000, 18500, 19000, 19500, 20000, 21000, 22000,
        24000, 25000, 26000, 27000, 28000, 29000, 30000, 32000, 34000, 36000, 38000, 40000,
        44000, 46000, 48000, 50000, 52000, 54000, 56000, 58000, 60000, 65000, 70000, 75000, 80000,
        
        # Specific bitshift result constants (from analysis)
        65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432,
        67108864, 134217728, 268435456, 536870912, 1073741824,
        
        # Powers of 2 related constants
        65535, 131071, 262143, 524287, 1048575, 2097151, 4194303, 8388607, 16777215, 33554431,
        
        # Common crypto constants
        0x10000, 0x20000, 0x40000, 0x80000, 0x100000, 0x200000, 0x400000, 0x800000,
        0x1000000, 0x2000000, 0x4000000, 0x8000000, 0x10000000, 0x20000000, 0x40000000,
    ]
    
    print("=== EXPANDED CONSTANTS ANALYSIS ===\n")
    
    print(f"Total constants: {len(large_constants):,}")
    print(f"Unique constants: {len(set(large_constants)):,}")
    print(f"Min value: {min(large_constants):,}")
    print(f"Max value: {max(large_constants):,}")
    
    # Check key predictions
    key_predictions = {
        "Position 18 predicted": 93887,
        "Original max": 158482,
        "1 million": 1000000,
        "100 million": 100000000, 
        "1 billion": 1000000000,
        "3 billion": 3000000000,
    }
    
    print(f"\nKey value coverage:")
    for name, value in key_predictions.items():
        included = value in large_constants
        status = "✓" if included else "✗"
        print(f"  {status} {name}: {value:,}")
    
    # Range analysis
    ranges = [
        ("Small (1K-10K)", 1000, 10000),
        ("Medium (10K-100K)", 10000, 100000),
        ("Large (100K-1M)", 100000, 1000000),
        ("Very Large (1M-10M)", 1000000, 10000000),
        ("Huge (10M-100M)", 10000000, 100000000),
        ("Massive (100M+)", 100000000, float('inf')),
    ]
    
    print(f"\nCoverage by range:")
    for name, min_val, max_val in ranges:
        count = sum(1 for c in large_constants if min_val <= c < max_val)
        print(f"  {name}: {count:,} constants")
    
    # Test the actual pattern
    print(f"\n=== TESTING KNOWN PATTERNS ===")
    
    known_keys = {11: 0x483, 12: 0xa7b, 13: 0x1460, 14: 0x2930, 15: 0x68f3, 16: 0xc936, 17: 0x1764f}
    
    for pos in range(12, 18):
        if pos in known_keys and pos-1 in known_keys:
            diff = known_keys[pos] - known_keys[pos-1]
            included = diff in large_constants
            status = "✓" if included else "✗"
            print(f"  {status} Position {pos-1}→{pos}: difference {diff:,} {'found' if included else 'MISSING'}")
    
    print(f"\n=== ESTIMATED FORMULA COUNT IMPACT ===")
    original_count = 8  # Original had 8 constants
    new_count = len(large_constants)
    impact = new_count - original_count
    
    print(f"Original constants: {original_count}")
    print(f"New constants: {new_count:,}")
    print(f"Additional formulas: +{impact:,} (each constant creates 2-3 formulas)")
    print(f"Total formula impact: ~+{impact * 2.5:,.0f} additional formulas")
    
    # Estimate performance impact
    original_total_formulas = 23050  # From the script output
    new_total_estimate = original_total_formulas + (impact * 2.5)
    print(f"Estimated total formulas: ~{new_total_estimate:,.0f}")
    performance_impact = (new_total_estimate / original_total_formulas - 1) * 100
    print(f"Performance impact: ~+{performance_impact:.1f}% more formulas to test")

if __name__ == "__main__":
    test_expanded_constants() 