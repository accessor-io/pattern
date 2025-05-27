#!/usr/bin/env python3

import sys
import os
import math

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solvers.archive.known_keys import KNOWN_KEYS

print("=== Mathematical Pattern Analysis of Keys ===\n")

# Calculate differences between consecutive keys
print("Approach 1: Differences between consecutive keys")
differences = []
for i in range(1, 66):
    if i in KNOWN_KEYS and i+1 in KNOWN_KEYS:
        current = KNOWN_KEYS[i]
        next_key = KNOWN_KEYS[i+1]
        difference = next_key - current
        differences.append(difference)
        print(f"Keys {i} -> {i+1}: Difference = {difference} (hex: {hex(difference)})")

# Check if differences follow a pattern
print("\nAnalyzing differences for patterns...")
# Is it a Fibonacci sequence?
if len(differences) >= 3:
    fibonacci = True
    for i in range(2, len(differences)):
        if differences[i] != differences[i-1] + differences[i-2]:
            fibonacci = False
            break
    print(f"Fibonacci pattern: {fibonacci}")

# Is it a geometric sequence?
if len(differences) >= 2:
    ratios = [differences[i]/differences[i-1] for i in range(1, len(differences))]
    geometric = all(abs(ratios[0] - ratio) < 0.001 for ratio in ratios)
    if geometric:
        print(f"Geometric sequence with ratio ≈ {ratios[0]}")
    else:
        print("Not a geometric sequence")

# Is it doubling?
if len(differences) >= 2:
    doubling = all(abs(differences[i] - 2*differences[i-1]) < 5 for i in range(1, len(differences)))
    print(f"Doubling pattern: {doubling}")

# Approach 2: Ratio between consecutive keys
print("\nApproach 2: Ratios between consecutive keys")
ratios = []
for i in range(1, 66):
    if i in KNOWN_KEYS and i+1 in KNOWN_KEYS:
        current = KNOWN_KEYS[i]
        next_key = KNOWN_KEYS[i+1]
        if current != 0:
            ratio = next_key / current
            ratios.append(ratio)
            print(f"Keys {i} -> {i+1}: Ratio = {ratio:.5f}")

# Check if the ratios are consistent
if len(ratios) >= 2:
    avg_ratio = sum(ratios) / len(ratios)
    std_dev = math.sqrt(sum((r - avg_ratio)**2 for r in ratios) / len(ratios))
    print(f"\nAverage ratio: {avg_ratio:.5f}")
    print(f"Standard deviation: {std_dev:.5f}")
    if std_dev < 0.5:
        print(f"Keys appear to follow a geometric sequence with ratio ≈ {avg_ratio:.5f}")
    else:
        print("Keys do not follow a consistent geometric sequence")

# Approach 3: Check for a specific pattern (each key is related to its index)
print("\nApproach 3: Looking for relationship between key value and its index")
relationships = []
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        # Try various formulas
        relationships.append((i, key, key/i, key/(i**2), key/(2**i)))

print("Key/Index Relationships:")
for idx, key, div_i, div_i2, div_2i in relationships[:10]:  # Show first 10
    print(f"Key {idx}: {hex(key)} | key/idx: {div_i:.5f} | key/idx²: {div_i2:.5f} | key/2^idx: {div_2i:.10f}")

# Formula hypothesis
hypothesis_match_count = 0
print("\nTesting hypothesis: key = 2^(idx+x) for some constant x")
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        # For 2^(idx+x) formula
        if key > 0:
            log2_key = math.log2(key)
            x_value = log2_key - i
            # Check if x_value is close to an integer
            if abs(x_value - round(x_value)) < 0.01:
                hypothesis_match_count += 1
                print(f"Key {i} fits formula: 2^({i}+{round(x_value)}) = {2**(i+round(x_value))}, Actual: {key}")

print(f"\nHypothesis matches: {hypothesis_match_count}/{len(KNOWN_KEYS)}")

# Checking if there's a mathematical formula connecting every 5th key
print("\nLooking for patterns in key subsequences...")
for step in range(2, 6):
    print(f"\nAnalyzing every {step}th key:")
    subsequence = [(i, KNOWN_KEYS[i]) for i in range(1, 67, step) if i in KNOWN_KEYS]
    if len(subsequence) > 2:
        for j in range(len(subsequence)-1):
            idx1, key1 = subsequence[j]
            idx2, key2 = subsequence[j+1]
            ratio = key2/key1 if key1 != 0 else float('inf')
            print(f"Keys {idx1} -> {idx2}: Ratio = {ratio:.5f}")

# Analyzing bit patterns
print("\nAnalyzing bit patterns in keys:")
for i in range(1, 67):
    if i in KNOWN_KEYS:
        key = KNOWN_KEYS[i]
        binary = bin(key)[2:]  # Remove '0b' prefix
        set_bits = binary.count('1')
        bit_length = len(binary)
        print(f"Key {i}: {bit_length} bits, {set_bits} bits set (density: {set_bits/bit_length:.2f})")

# Check if the keys, when treated as ASCII and concatenated, form a meaningful message
print("\nChecking for hidden message in digits:")
key_digits = ''.join([str(KNOWN_KEYS[i]) for i in range(1, 67) if i in KNOWN_KEYS])
print(f"Concatenated digits: {key_digits[:50]}...") # First 50 digits

# Get the first digit of each key and see if they form a pattern
first_digits = [str(KNOWN_KEYS[i])[0] for i in range(1, 67) if i in KNOWN_KEYS]
print(f"First digits: {''.join(first_digits)}")

# Compute Fibonacci Numbers up to the largest key and check if keys match
max_key = max(KNOWN_KEYS.values())
fibs = [0, 1]
while fibs[-1] < max_key:
    fibs.append(fibs[-1] + fibs[-2])

fib_matches = []
for i in range(1, 67):
    if i in KNOWN_KEYS and KNOWN_KEYS[i] in fibs:
        fib_index = fibs.index(KNOWN_KEYS[i])
        fib_matches.append((i, fib_index))

print("\nKeys matching Fibonacci numbers:")
for key_idx, fib_idx in fib_matches:
    print(f"Key {key_idx} ({hex(KNOWN_KEYS[key_idx])}) = Fibonacci({fib_idx}) = {fibs[fib_idx]}")

# Check for prime number relationships
print("\nChecking if keys are prime numbers:")
def is_prime(n):
    """Check if a number is prime (simple implementation)"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

prime_keys = []
for i in range(1, 67):
    if i in KNOWN_KEYS and is_prime(KNOWN_KEYS[i]):
        prime_keys.append(i)

print(f"Prime number keys: {prime_keys}")

# Final analysis: look for base64/base32 strings
print("\nConcatenating keys in chunks and checking for ASCII:")
all_keys_hex = ''.join([hex(KNOWN_KEYS[i])[2:].zfill(8) for i in range(1, 67) if i in KNOWN_KEYS])
try:
    # Try to decode chunks of 2 bytes
    for chunk_size in [2, 4, 8]:
        print(f"\nDecoding {chunk_size}-byte chunks:")
        chunks = [all_keys_hex[i:i+chunk_size*2] for i in range(0, len(all_keys_hex), chunk_size*2)]
        for i, chunk in enumerate(chunks[:10]):  # Show first 10 chunks
            try:
                byte_data = bytes.fromhex(chunk)
                ascii_repr = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in byte_data)
                print(f"Chunk {i}: {chunk} -> {ascii_repr}")
            except:
                pass
except Exception as e:
    print(f"Error in decoding: {e}") 