#!/usr/bin/env python3
"""
Advanced analysis script for Bitcoin private key patterns
"""

import hashlib
import binascii
import base58
from typing import List, Tuple

def decode_base58_privkey(b58_key: str) -> bytes:
    """Properly decode a Base58 private key to raw bytes."""
    try:
        # Remove the version byte (0x80) and checksum
        raw_bytes = base58.b58decode(b58_key)
        # Return just the 32-byte private key
        return raw_bytes[1:-4]
    except Exception as e:
        print(f"Error decoding key {b58_key}: {str(e)}")
        return None

def analyze_key_patterns(keys: List[str]) -> None:
    """Analyze various patterns between consecutive keys."""
    for i in range(len(keys) - 1):
        current_key = decode_base58_privkey(keys[i])
        next_key = decode_base58_privkey(keys[i + 1])
        
        if current_key is None or next_key is None:
            continue
            
        # Convert to integers
        current_int = int.from_bytes(current_key, 'big')
        next_int = int.from_bytes(next_key, 'big')
        
        # Try different operations
        diff = (next_int - current_int) % (2**256)
        xor = current_int ^ next_int
        and_op = current_int & next_int
        or_op = current_int | next_int
        
        print(f"\nPair {i} -> {i+1}:")
        print(f"Current:  {keys[i]}")
        print(f"Next:     {keys[i+1]}")
        print(f"Raw diff: {hex(diff)}")
        print(f"XOR:      {hex(xor)}")
        print(f"AND:      {hex(and_op)}")
        print(f"OR:       {hex(or_op)}")
        
        # Look for patterns in 32-bit segments
        current_segments = [current_int >> (i * 32) & 0xFFFFFFFF for i in range(8)]
        next_segments = [next_int >> (i * 32) & 0xFFFFFFFF for i in range(8)]
        
        print("\n32-bit segments:")
        for j in range(8):
            print(f"Segment {j}: {hex(current_segments[j])} -> {hex(next_segments[j])}")
            print(f"Segment {j} diff: {hex((next_segments[j] - current_segments[j]) % (2**32))}")

def main():
    # Read the puzzle file
    with open("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb", 'r') as f:
        lines = f.readlines()
    
    # Extract private keys (every other line)
    private_keys = [line.strip() for i, line in enumerate(lines) if i % 2 == 0]
    
    print("Analyzing key patterns...\n")
    analyze_key_patterns(private_keys[:10])  # Start with first 10 keys for initial analysis

if __name__ == "__main__":
    main() 