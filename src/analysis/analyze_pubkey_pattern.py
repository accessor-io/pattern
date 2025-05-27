#!/usr/bin/env python3
"""
Analyze patterns in the public keys of the Bitcoin puzzle
"""

import hashlib
import binascii
import base58
from typing import List, Tuple

# The test value
TEST_VALUE = 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313

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

def analyze_pubkey_patterns(pairs: List[Tuple[str, str]]) -> None:
    """Analyze patterns in public keys."""
    print("Analyzing public key patterns...\n")
    
    for i in range(len(pairs) - 1):
        current_pub = pairs[i][1]
        next_pub = pairs[i + 1][1]
        
        print(f"\nPair {i} -> {i+1}:")
        print(f"Current private: {pairs[i][0]}")
        print(f"Current public:  {current_pub}")
        print(f"Next private:    {pairs[i+1][0]}")
        print(f"Next public:     {next_pub}")
        
        # Look for patterns in the public key encoding
        try:
            current_bytes = base58.b58decode(current_pub)
            next_bytes = base58.b58decode(next_pub)
            
            # Convert to hex for analysis
            current_hex = current_bytes.hex()
            next_hex = next_bytes.hex()
            test_hex = hex(TEST_VALUE)[2:].zfill(64)
            
            print(f"\nPublic key bytes:")
            print(f"Current: {current_hex}")
            print(f"Next:    {next_hex}")
            
            # Look for the test value in the differences
            diff = int(next_hex, 16) ^ int(current_hex, 16)
            print(f"\nXOR difference: {hex(diff)}")
            
            # Check if test value appears in any part of the public keys
            if test_hex in current_hex or test_hex in next_hex:
                print(f"Found test value in public key!")
                print(f"Position in current: {current_hex.find(test_hex)}")
                print(f"Position in next: {next_hex.find(test_hex)}")
            
            # Look for patterns in 32-byte segments
            current_segments = [current_hex[i:i+64] for i in range(0, len(current_hex), 64)]
            next_segments = [next_hex[i:i+64] for i in range(0, len(next_hex), 64)]
            
            print("\nSegment analysis:")
            for j, (curr_seg, next_seg) in enumerate(zip(current_segments, next_segments)):
                if curr_seg and next_seg:
                    seg_diff = int(next_seg, 16) ^ int(curr_seg, 16)
                    print(f"Segment {j} XOR: {hex(seg_diff)}")
                    
                    # Check if segment difference matches any part of our test value
                    if hex(seg_diff)[2:] in test_hex:
                        print(f"Found matching pattern in segment {j}!")
                        print(f"Segment diff: {hex(seg_diff)}")
                        print(f"Test value:   {test_hex}")
            
        except Exception as e:
            print(f"Error analyzing public keys: {str(e)}")

def main():
    pairs = read_key_pairs("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb")
    print(f"Testing with value: {hex(TEST_VALUE)}\n")
    analyze_pubkey_patterns(pairs[:10])  # Analyze first 10 pairs

if __name__ == "__main__":
    main() 