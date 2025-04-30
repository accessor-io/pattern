#!/usr/bin/env python3
"""
Test script to verify the cryptographic difference pattern
0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313
"""

import hashlib
import binascii
from typing import List, Tuple

# The difference value we're testing
DIFF_VALUE = 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313

def read_key_pairs(filename: str) -> List[Tuple[str, str]]:
    """Read private/public key pairs from the puzzle file."""
    pairs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                priv = lines[i].strip()
                pub = lines[i + 1].strip()
                pairs.append((priv, pub))
    return pairs

def hex_to_int(hex_str: str) -> int:
    """Convert a hex string to integer."""
    return int(hex_str, 16)

def test_difference_pattern(pairs: List[Tuple[str, str]]) -> List[bool]:
    """
    Test if the difference between consecutive private keys matches our DIFF_VALUE.
    Returns a list of boolean values indicating where the pattern matches.
    """
    results = []
    for i in range(len(pairs) - 1):
        current_priv = hex_to_int(pairs[i][0])
        next_priv = hex_to_int(pairs[i + 1][0])
        
        # Calculate difference
        diff = (next_priv - current_priv) % (2**256)
        
        # Check if it matches our expected difference
        matches = diff == DIFF_VALUE
        results.append(matches)
        
        print(f"Pair {i} -> {i+1}:")
        print(f"Current:  {pairs[i][0]}")
        print(f"Next:     {pairs[i+1][0]}")
        print(f"Diff:     {hex(diff)}")
        print(f"Matches:  {matches}\n")
    
    return results

def main():
    # Read the puzzle file
    pairs = read_key_pairs("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb")
    
    print(f"Testing difference pattern with value: {hex(DIFF_VALUE)}\n")
    
    # Test the pattern
    results = test_difference_pattern(pairs)
    
    # Summarize results
    matches = sum(results)
    total = len(results)
    print(f"\nSummary:")
    print(f"Pattern matches: {matches} out of {total} consecutive pairs")
    print(f"Match rate: {(matches/total)*100:.2f}%")

if __name__ == "__main__":
    main() 