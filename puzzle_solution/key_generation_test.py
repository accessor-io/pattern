#!/usr/bin/env python3
"""
Test if 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313
is used in generating consecutive Bitcoin private keys
"""

import hashlib
import binascii
import base58
from typing import List, Tuple

# The value we're testing
TEST_VALUE = 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313

def decode_privkey(key: str) -> bytes:
    """Decode a Base58 private key, handling both compressed and uncompressed formats."""
    try:
        raw = base58.b58decode(key)
        # Remove version byte (0x80) and checksum (last 4 bytes)
        # If compressed format (has 0x01 byte), remove that too
        if len(raw) == 38:  # compressed format
            return raw[1:-5]
        return raw[1:-4]  # uncompressed format
    except Exception as e:
        print(f"Error decoding {key}: {e}")
        return None

def test_key_generation_patterns(keys: List[str]) -> None:
    """Test various ways the value might be used in key generation."""
    print("Testing key generation patterns...")
    
    for i in range(len(keys) - 1):
        current = decode_privkey(keys[i])
        next_key = decode_privkey(keys[i + 1])
        
        if not current or not next_key:
            continue
            
        current_int = int.from_bytes(current, 'big')
        next_int = int.from_bytes(next_key, 'big')
        
        # Test different operations that might generate the next key
        tests = {
            "Addition": (current_int + TEST_VALUE) % (2**256),
            "Subtraction": (current_int - TEST_VALUE) % (2**256),
            "XOR": current_int ^ TEST_VALUE,
            "Addition of segments": 0,
            "Multiplication mod N": (current_int * TEST_VALUE) % (2**256),
        }
        
        # Test addition of 32-bit segments
        current_segments = [current_int >> (j * 32) & 0xFFFFFFFF for j in range(8)]
        test_segments = [TEST_VALUE >> (j * 32) & 0xFFFFFFFF for j in range(8)]
        segment_sum = sum((a + b) % (2**32) << (j * 32) 
                         for j, (a, b) in enumerate(zip(current_segments, test_segments)))
        tests["Addition of segments"] = segment_sum % (2**256)
        
        print(f"\nAnalyzing pair {i} -> {i+1}:")
        print(f"Current key:  {keys[i]}")
        print(f"Next key:     {keys[i+1]}")
        print(f"Current (hex): {hex(current_int)}")
        print(f"Next (hex):    {hex(next_int)}")
        print("\nTesting operations:")
        
        for op_name, result in tests.items():
            matches = result == next_int
            if matches:
                print(f"✓ MATCH FOUND! {op_name} generates the next key!")
            print(f"{op_name}:")
            print(f"  Expected: {hex(next_int)}")
            print(f"  Got:      {hex(result)}")
            print(f"  Matches:  {matches}")
        
        # Also test if the value appears in any part of the key
        current_bytes = current.hex()
        next_bytes = next_key.hex()
        test_bytes = hex(TEST_VALUE)[2:].zfill(64)
        
        print("\nSearching for value in key bytes:")
        for j in range(0, len(current_bytes) - len(test_bytes) + 1, 2):
            segment = current_bytes[j:j+len(test_bytes)]
            if segment in test_bytes or test_bytes in segment:
                print(f"Found partial match at position {j//2} in current key!")
                print(f"Segment: {segment}")
                print(f"Test:    {test_bytes}")

def main():
    # Read keys from puzzle file
    with open("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb", 'r') as f:
        keys = [line.strip() for i, line in enumerate(f) if i % 2 == 0]
    
    print(f"Testing with value: {hex(TEST_VALUE)}\n")
    test_key_generation_patterns(keys[:20])  # Test first 20 keys

if __name__ == "__main__":
    main() 