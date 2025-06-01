#!/usr/bin/env python3
"""
Find the actual constants for intermediate Bitcoin puzzle positions.
We know the pattern is k[n] = k[n-1] + constant[n].
We need to find the constants for positions 71-74, 76-79, etc.
"""

import sys

# Load verified keys from file
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
except Exception as e:
    print(f"Error loading verified keys: {e}")
    sys.exit(1)

print("=== FINDING CONSTANTS FOR INTERMEDIATE POSITIONS ===")
print()

# First, let's analyze the constants for known positions to find the pattern
print("Known constants (differences between consecutive positions):")
constants = {}
for pos in sorted(verified_keys.keys()):
    if pos > 1 and pos - 1 in verified_keys:
        const = verified_keys[pos] - verified_keys[pos - 1]
        constants[pos] = const
        if pos <= 20 or pos % 5 == 0 or pos in [68, 69, 70]:
            print(f"Position {pos}: constant = {const:,}")

# Analyze growth pattern
print("\n=== ANALYZING GROWTH PATTERN ===")
print("\nGrowth factors between consecutive constants:")
growth_factors = []
prev_const = None
prev_pos = None
for pos in sorted(constants.keys()):
    if prev_const and prev_const > 0:
        growth = constants[pos] / prev_const
        growth_factors.append((prev_pos, pos, growth))
        if pos <= 30 or pos >= 65:
            print(f"Pos {prev_pos}->{pos}: {growth:.4f}x")
    prev_const = constants[pos]
    prev_pos = pos

# Analyze growth around positions 70 and 75
print("\n=== FOCUS ON POSITIONS 69-75 ===")
for pos in range(69, 76):
    if pos in constants:
        print(f"Position {pos}: constant = {constants[pos]:,}")

# Calculate growth between 70 and 75
if 70 in constants and 75 in verified_keys and 74 in verified_keys:
    # We need to find the total growth from 70 to 75
    key_70 = verified_keys[70]
    key_75 = verified_keys[75]
    total_diff = key_75 - key_70
    print(f"\nTotal difference from pos 70 to 75: {total_diff:,}")
    
    # This is the sum of constants for positions 71, 72, 73, 74, 75
    # constant[71] + constant[72] + constant[73] + constant[74] + constant[75]
    
    # Let's check if we have the actual constants for some of these positions
    # from the GENERATED values in the file
    print("\nChecking for GENERATED values in positions 71-74:")
    for pos in range(71, 75):
        if pos in verified_keys:
            const = verified_keys[pos] - verified_keys[pos - 1]
            print(f"  Position {pos}: key = 0x{verified_keys[pos]:x}, constant = {const:,}")

# Try to estimate based on geometric growth
print("\n=== ESTIMATING CONSTANTS USING GEOMETRIC GROWTH ===")

# Method 1: Simple geometric progression
# Find average growth rate around position 70
recent_growth_rates = []
for pos in range(65, 71):
    if pos in constants and pos - 1 in constants and constants[pos - 1] > 0:
        growth = constants[pos] / constants[pos - 1]
        recent_growth_rates.append(growth)
        print(f"Growth {pos-1}->{pos}: {growth:.4f}")

if recent_growth_rates:
    avg_growth = sum(recent_growth_rates) / len(recent_growth_rates)
    print(f"\nAverage growth rate around pos 70: {avg_growth:.4f}")
    
    # Use this to estimate constants
    if 70 in constants:
        print("\nEstimated constants using geometric growth:")
        base_const = constants[70]
        for i in range(1, 6):
            est_const = int(base_const * (avg_growth ** i))
            print(f"  Position {70 + i}: ~{est_const:,}")

# Method 2: Check if the growth itself follows a pattern
print("\n=== ANALYZING GROWTH PATTERN CHANGES ===")
print("Looking for patterns in how growth rate changes...")

# Group growth factors by position ranges
print("\nGrowth factors by range:")
ranges = [(2, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70)]
for start, end in ranges:
    range_growths = []
    for pos, next_pos, growth in growth_factors:
        if start <= pos < end:
            range_growths.append(growth)
    if range_growths:
        avg = sum(range_growths) / len(range_growths)
        print(f"Positions {start}-{end}: avg growth = {avg:.4f}")

# Try to find the actual values from the expected addresses
print("\n=== ATTEMPTING TO DERIVE FROM EXPECTED ADDRESSES ===")
print("(This would require brute-forcing the private keys, which is computationally infeasible)")
print("The Bitcoin puzzle is designed so that you cannot derive private keys from addresses.")
print("\nThe only way to find the intermediate keys is to:")
print("1. Solve the actual Bitcoin puzzles (computationally hard)")
print("2. Find the mathematical pattern that generates the sequence")
print("3. Use known solutions if they've been published")

# Check if there's a pattern in the constants themselves
print("\n=== CHECKING FOR PATTERNS IN CONSTANTS ===")
print("Checking if constants follow arithmetic or other progressions...")

# Check differences between consecutive constants
const_diffs = []
prev_const = None
for pos in sorted(constants.keys())[:30]:  # First 30 positions
    if prev_const is not None:
        diff = constants[pos] - prev_const
        const_diffs.append((pos, diff))
        print(f"constant[{pos}] - constant[{pos-1}] = {diff}")
    prev_const = constants[pos]

# Summary
print("\n=== SUMMARY ===")
print("The Bitcoin puzzle uses a deterministic pattern, but without the actual")
print("private keys for positions 71-74, 76-79, etc., we cannot determine the exact constants.")
print("\nPossible approaches:")
print("1. If these positions were solved and published, use those values")
print("2. If there's a hidden pattern in the constants, discover it")
print("3. Brute force search (computationally infeasible for high positions)")

# Output what we know for certain
print("\n=== KNOWN CONSTANTS FOR REFERENCE ===")
known_ranges = [(1, 70), (75, 75), (80, 80), (85, 85), (90, 90), (95, 95), (100, 100), 
                (110, 110), (115, 115), (120, 120), (125, 125), (130, 130)]
for start, end in known_ranges:
    for pos in range(start, end + 1):
        if pos in constants:
            print(f"Position {pos}: {constants[pos]:,}") 