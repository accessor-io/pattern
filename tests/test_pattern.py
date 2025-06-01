#!/usr/bin/env python3
"""
Testing the 'Rotate left 1 and XOR with previous' pattern identified in sequence analysis.
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import sys

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known sequence terms
TERM_66 = 0x2832ed74f2b5e35ee
TERM_67 = 0x730fc235c1942c1ae

# Alternative value from analysis logs
TERM_67_ALT = 0x3ce0e3395f140001

def rotate_left(value, bits, bit_length=64):
    """Rotate the bits of 'value' left by 'bits' positions"""
    return ((value << bits) | (value >> (bit_length - bits))) & ((1 << bit_length) - 1)

def generate_candidates():
    """Generate candidates based on the rotate-and-XOR pattern"""
    candidates = []
    
    # Basic pattern: Rotate left 1 and XOR with previous
    # Using both versions of Term 67
    for term_67 in [TERM_67, TERM_67_ALT]:
        # For various bit lengths and rotation amounts
        for bit_length in [64, 68, 70, 72, 80, 96, 128]:
            for rotate_bits in range(1, 9):
                # Try direct rotation + XOR
                rotated = rotate_left(term_67, rotate_bits, bit_length)
                candidate1 = rotated ^ TERM_66
                candidates.append(candidate1)
                
                # Try rotation + XOR but with term_66 first
                rotated_66 = rotate_left(TERM_66, rotate_bits, bit_length)
                candidate2 = rotated_66 ^ term_67
                candidates.append(candidate2)
                
                # Try rotation and addition
                candidate3 = rotated + TERM_66
                candidates.append(candidate3)
                
                # Try double rotation
                rotated_again = rotate_left(rotated, rotate_bits, bit_length)
                candidate4 = rotated_again ^ TERM_66
                candidates.append(candidate4)
                
    # Deduplication
    return list(set(candidates))

def private_key_to_address(private_key):
    """Convert a private key (integer) to a compressed Bitcoin address."""
    try:
        # Convert integer to bytes
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Create ECDSA signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get x and y coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create compressed public key format (0x02 if y is even, 0x03 if y is odd)
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        compressed_pubkey = prefix + x.to_bytes(32, 'big')
        
        # Hash with SHA-256 and RIPEMD-160
        sha_digest = hashlib.sha256(compressed_pubkey).digest()
        try:
            ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        except Exception:
            # Fallback for environments without ripemd160
            ripemd_digest = hashlib.sha256(sha_digest).digest()[:20]
            
        # Add network byte (0x00 for mainnet)
        versioned_payload = b'\x00' + ripemd_digest
        
        # Calculate and append checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Encode with Base58
        address = base58.b58encode(address_bytes).decode('utf-8')
        return address
    except Exception as e:
        print(f"Error generating address: {e}")
        return None

def save_result(private_key):
    """Save the found private key to both JSON and text files"""
    import json
    
    result = {
        "term_index": 68,
        "private_key_hex": hex(private_key),
        "private_key_int": private_key,
        "bitcoin_address": TARGET_ADDRESS,
        "found_timestamp": time.time(),
        "human_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save as JSON
    with open("term68_solution.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Save as text file
    with open("term68_solution.txt", "w") as f:
        f.write(f"Term 68 Solution\n")
        f.write(f"Private Key (hex): {hex(private_key)}\n")
        f.write(f"Private Key (int): {private_key}\n")
        f.write(f"Bitcoin Address: {TARGET_ADDRESS}\n")
        
    print(f"Solution saved to term68_solution.json and term68_solution.txt")
    
    # Also print to screen
    print("\n=== PRIVATE KEY FOUND! ===")
    print(f"Term 68: {hex(private_key)}")
    print(f"Bitcoin Address: {TARGET_ADDRESS}")
    
    return result

def test_pattern_candidates():
    """Test candidates generated from the rotate-and-XOR pattern"""
    candidates = generate_candidates()
    print(f"Generated {len(candidates)} candidates from pattern")
    
    for i, candidate in enumerate(candidates):
        print(f"Testing candidate {i+1}/{len(candidates)}: {hex(candidate)}")
        address = private_key_to_address(candidate)
        if address == TARGET_ADDRESS:
            print(f"MATCH FOUND! Candidate: {hex(candidate)}")
            return candidate
            
    print("No match found in pattern-generated candidates")
    return None

if __name__ == "__main__":
    print("Starting pattern-based search for position 68")
    start_time = time.time()
    
    result = test_pattern_candidates()
    
    if result:
        save_result(result)
    else:
        print("\nNo solution found.")
        
    print(f"Search completed in {time.time() - start_time:.2f} seconds") 