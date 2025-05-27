#!/usr/bin/env python3

import os
import sys
import hashlib
import binascii
from typing import Dict, List, Tuple, Optional

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_known_keys() -> Dict[int, int]:
    """Load the known keys from the module"""
    try:
        from solvers.archive.known_keys import KNOWN_KEYS
        return KNOWN_KEYS
    except Exception as e:
        print(f"Error loading KNOWN_KEYS: {e}")
        return {}

def verify_keys_directly():
    """Simply compare candidate private keys with known keys directly"""
    known_keys = load_known_keys()
    if not known_keys:
        print("Failed to load known keys. Cannot verify.")
        return
    
    print(f"Loaded {len(known_keys)} known keys.")
    
    # Display the first few known keys
    print("\nKnown Keys (first 5):")
    for i in range(1, min(6, len(known_keys) + 1)):
        if i in known_keys:
            print(f"Key {i}: 0x{known_keys[i]:x}")
    
    # Load candidate private keys from file
    candidates = []
    try:
        with open("derived_private_keys.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(" -> ")
                if len(parts) != 2:
                    continue
                
                private_key_str, key_info = parts
                
                # Extract key index
                if "Key " in key_info:
                    try:
                        key_index = int(key_info.split("Key ")[1].split(" ")[0])
                        private_key_int = int(private_key_str)
                        candidates.append((key_index, private_key_int, key_info))
                    except:
                        pass
    except Exception as e:
        print(f"Error loading candidate private keys: {e}")
        return
    
    print(f"\nLoaded {len(candidates)} candidate private keys")
    
    # Direct comparison
    matches = []
    for key_index, candidate_key, key_info in candidates:
        if key_index in known_keys:
            known_key = known_keys[key_index]
            
            if candidate_key == known_key:
                matches.append((key_index, candidate_key, key_info))
                print(f"✓ MATCH: Key {key_index} - Candidate {candidate_key} matches known key 0x{known_key:x}")
            else:
                # Print just a few mismatches as examples
                if len(matches) + len(matches) < 5:
                    print(f"✗ MISMATCH: Key {key_index} - Candidate {candidate_key} ≠ Known 0x{known_key:x}")
    
    # Summarize matches
    if matches:
        print(f"\nFound {len(matches)} private keys that match known keys:")
        for key_index, private_key, key_info in matches:
            print(f"Key {key_index}: {private_key} -> {key_info}")
    else:
        print("\nNo matching private keys found.")
        print("This suggests that:")
        print("1. The 'known_keys' in the puzzle are not the actual private keys")
        print("2. There is a transformation relationship between known_keys and private keys")
        print("3. Additional cryptographic steps are needed to derive private keys")
    
    # Check if the known keys are directly valid private keys
    print("\nVerifying if known keys are valid private keys themselves:")
    for i in range(1, min(5, len(known_keys) + 1)):
        if i in known_keys:
            key_value = known_keys[i]
            if 1 <= key_value < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141:
                print(f"Key {i}: 0x{key_value:x} is within valid private key range")
            else:
                print(f"Key {i}: 0x{key_value:x} is NOT within valid private key range")

def main():
    print("Bitcoin Private Key Direct Verification Tool")
    print("===========================================")
    verify_keys_directly()

if __name__ == "__main__":
    main() 