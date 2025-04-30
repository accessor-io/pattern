#!/usr/bin/env python3

import os
import sys
import hashlib
import binascii
from typing import Dict, List, Tuple, Optional

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_keys_from_sequence() -> Dict[int, int]:
    """Load all 160 keys from the verified Bitcoin sequence"""
    # Try to import directly from the module
    try:
        from solvers.archive.known_keys import KNOWN_KEYS
        print("Successfully loaded keys from known_keys module")
        return KNOWN_KEYS
    except Exception as e:
        print(f"Error importing from module: {e}")
    
    # If that fails, try to read the file manually
    sequence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "hex_sequence_analysis", "verified_bitcoin_sequence.txt")
    
    keys = {}
    try:
        with open(sequence_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('. ')
                if len(parts) != 2:
                    continue
                    
                index = int(parts[0])
                key_str = parts[1].strip()
                
                # Remove the " - KNOWN" suffix if present
                if " - KNOWN" in key_str:
                    key_str = key_str.split(" - KNOWN")[0].strip()
                
                # Try to convert to integer
                try:
                    # If it's a hex string, convert it
                    if key_str.startswith("0x"):
                        keys[index] = int(key_str, 16)
                    else:
                        keys[index] = int(key_str, 16)
                except ValueError:
                    print(f"Warning: Could not parse key {index}: {key_str}")
                    
        print(f"Loaded {len(keys)} keys from file: {sequence_path}")
    except Exception as e:
        print(f"Error loading keys from file: {e}")
    
    return keys

def get_bit_patterns(number: int) -> List[int]:
    """Analyze the bit patterns in a number"""
    bit_patterns = []
    binary = bin(number)[2:]  # Remove '0b' prefix
    
    # Record runs of 1s
    run_length = 0
    for bit in binary:
        if bit == '1':
            run_length += 1
        else:
            if run_length > 0:
                bit_patterns.append(run_length)
                run_length = 0
    
    # Don't forget the last run if it exists
    if run_length > 0:
        bit_patterns.append(run_length)
    
    return bit_patterns

def analyze_key_patterns(keys: Dict[int, int]) -> List[Tuple[str, str]]:
    """Analyze keys for patterns that might reveal private keys"""
    print(f"Analyzing {len(keys)} keys for patterns...")
    
    # Look for mathematical relationships
    private_keys = []
    
    # Check if first few keys follow Fibonacci
    fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    matches = 0
    for i in range(min(len(keys), len(fibonacci))):
        if i+1 in keys and keys[i+1] == fibonacci[i]:
            matches += 1
    
    fibonacci_match = matches > len(fibonacci) // 2
    
    if fibonacci_match:
        print(f"Keys follow Fibonacci sequence with {matches} matches!")
        # Try using Fibonacci sequence as private keys
        for i in range(1, len(keys) + 1):
            if i <= len(fibonacci):
                private_key = fibonacci[i-1]
                public_key = f"Key {i} (Fibonacci {i})"
                private_keys.append((str(private_key), public_key))
    
    # Alternative approaches:
    
    # 1. Check for sequential increments
    increments = []
    for i in range(1, min(10, len(keys))):  # Check just first few keys
        if i in keys and i+1 in keys:
            current = keys[i]
            next_key = keys[i+1]
            increment = next_key - current
            increments.append(increment)
            print(f"Key {i} to {i+1}: {hex(current)} -> {hex(next_key)}, diff: {increment}")
    
    if increments and len(set(increments)) <= 3:  # If most increments are similar
        common_increment = max(set(increments), key=increments.count)
        print(f"Keys appear to follow an increment pattern, most common: {common_increment}")
        # Create private keys based on this pattern
        for i in range(1, len(keys) + 1):
            if i in keys:
                private_key = i * common_increment
                public_key = f"Key {i} (increment pattern)"
                private_keys.append((str(private_key), public_key))
    
    # 2. Try bit patterns
    bit_pattern_consistency = []
    for i in range(1, min(10, len(keys))):
        if i in keys:
            patterns = get_bit_patterns(keys[i])
            print(f"Key {i}: {hex(keys[i])} -> Bit patterns: {patterns}")
            bit_pattern_consistency.append(patterns)
    
    # If the bit patterns show consistency, try using them
    if bit_pattern_consistency and all(len(p) > 0 for p in bit_pattern_consistency):
        print("Keys show consistent bit patterns")
        # Use bit patterns as a basis for private keys
        for i in range(1, len(keys) + 1):
            if i in keys:
                patterns = get_bit_patterns(keys[i])
                if patterns:
                    private_key = sum(patterns)  # Sum of bit runs as a simple derivation
                    public_key = f"Key {i} (bit pattern)"
                    private_keys.append((str(private_key), public_key))
    
    # 3. Check if keys are related to their index
    index_relations = []
    for i in range(1, min(10, len(keys))):
        if i in keys:
            key = keys[i]
            relation = key // i if i != 0 else 0
            index_relations.append(relation)
            print(f"Key {i}: {hex(key)} -> Relation to index: {relation}")
    
    if index_relations and len(set(index_relations)) <= 3:
        common_relation = max(set(index_relations), key=index_relations.count)
        print(f"Keys appear related to their indices, common factor: {common_relation}")
        # Create private keys based on this pattern
        for i in range(1, len(keys) + 1):
            private_key = i * common_relation
            public_key = f"Key {i} (index relation)"
            private_keys.append((str(private_key), public_key))
    
    # Check for ASCII patterns in the keys
    try:
        from solvers.archive.known_keys import convert_significant_bits_to_ascii
        print("\nChecking for ASCII patterns in keys:")
        for i in range(1, min(10, len(keys))):
            if i in keys:
                key = keys[i]
                ascii_str = convert_significant_bits_to_ascii(key)
                print(f"Key {i}: ASCII = {ascii_str}")
                
                # If we find meaningful ASCII, use the ASCII code as a hint
                if any(c.isalpha() for c in ascii_str):
                    private_key = int.from_bytes(ascii_str.encode(), 'big')
                    public_key = f"Key {i} (ASCII: {ascii_str})"
                    private_keys.append((str(private_key), public_key))
    except Exception as e:
        print(f"Error checking ASCII patterns: {e}")
    
    # If we have the hidden Bitcoin address, try to use it as a clue
    hidden_address = "1CZqucvN1wZ4Gwq95dsNgj1xVjUcK3pcMQ"
    try:
        import base58
        decoded = base58.b58decode(hidden_address)
        if len(decoded) == 25:
            version = decoded[0]
            hash160 = decoded[1:21]
            checksum = decoded[21:25]
            
            print(f"\nTrying to use hidden address as a clue:")
            print(f"Version: {version}, Hash160: {hash160.hex()}, Checksum: {checksum.hex()}")
            
            # Try hash160 as a private key seed
            for i in range(1, len(keys) + 1):
                private_key = int.from_bytes(hash160, 'big') + i
                public_key = f"Key {i} (hash160 derived)"
                private_keys.append((str(private_key), public_key))
    except Exception as e:
        print(f"Error using hidden address: {e}")
    
    return private_keys

def verify_private_key(private_key: str, expected_public_key: Optional[str] = None) -> bool:
    """Verify if a private key derives to the expected public key"""
    # This would require implementing Bitcoin's ECDSA key derivation
    # which is beyond the scope of this demonstration
    print(f"Would verify private key: {private_key}")
    return True  # Placeholder

def main():
    keys = load_keys_from_sequence()
    if not keys:
        print("No keys found. Exiting.")
        return
    
    print(f"Loaded {len(keys)} keys.")
    
    # Display first few keys to verify
    print("\nFirst few keys:")
    for i in range(1, min(6, len(keys) + 1)):
        key_str = hex(keys.get(i, 0))
        print(f"Key {i}: {key_str}")
    
    # Try to derive private keys
    private_keys = analyze_key_patterns(keys)
    
    if private_keys:
        print("\nPossible private keys derived:")
        for i, (private_key, public_key) in enumerate(private_keys[:10]):
            print(f"{i+1}: Private: {private_key} -> {public_key}")
        
        if len(private_keys) > 10:
            print(f"... and {len(private_keys) - 10} more")
        
        # Save to file
        with open("derived_private_keys.txt", "w") as f:
            for private_key, public_key in private_keys:
                f.write(f"{private_key} -> {public_key}\n")
        
        print(f"\nSaved {len(private_keys)} potential derived keys to derived_private_keys.txt")
        print("\nNOTE: These are speculative keys based on patterns. They may not be the actual private keys.")
        print("To verify, you would need to derive the public keys and Bitcoin addresses from these private keys.")
    else:
        print("\nCould not derive private keys using simple patterns.")
        print("This likely requires more advanced cryptographic techniques or specific knowledge.")
        print("Consider trying:")
        print("1. Specialized Bitcoin key derivation algorithms")
        print("2. Looking for encoded hints in the puzzle itself")
        print("3. Retracing cryptographic steps from the final solution backward")

if __name__ == "__main__":
    main() 