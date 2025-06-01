#!/usr/bin/env python3
"""
Create Kangaroo input file for Position 71 search
Uses predicted private key 0x40760c9d7ecaf1f800 to generate public key
"""

import hashlib
from ecdsa import SigningKey, SECP256k1

# Predicted private key for position 71
PREDICTED_KEY_71 = 0x40760c9d7ecaf1f800
TARGET_ADDRESS_71 = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

def private_key_to_public_key(private_key: int) -> str:
    """Convert private key to uncompressed public key hex"""
    privkey_hex = format(private_key, '064x')
    privkey_bytes = bytes.fromhex(privkey_hex)
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    # Uncompressed public key format (0x04 + x + y)
    pubkey = '04' + format(x, '064x') + format(y, '064x')
    return pubkey

def create_kangaroo_input():
    """Create input file for Kangaroo search"""
    
    print(f"Creating Kangaroo input for Position 71")
    print(f"Predicted private key: 0x{PREDICTED_KEY_71:x}")
    print(f"Target address: {TARGET_ADDRESS_71}")
    
    # Convert predicted private key to public key
    public_key = private_key_to_public_key(PREDICTED_KEY_71)
    print(f"Generated public key: {public_key}")
    
    # Set search range around predicted value
    # Use a range of ±2^20 around the predicted value for reasonable search time
    range_size = 2**20  # About 1 million keys on each side
    start_range = max(1, PREDICTED_KEY_71 - range_size)
    end_range = PREDICTED_KEY_71 + range_size
    
    print(f"Search range: 0x{start_range:x} to 0x{end_range:x}")
    print(f"Range size: {end_range - start_range:,} keys")
    
    # Create Kangaroo input file
    with open('Kangaroo/puzzle71_input.txt', 'w') as f:
        f.write(f"{start_range:x}\n")
        f.write(f"{end_range:x}\n") 
        f.write(f"{public_key}\n")
    
    print(f"Created Kangaroo input file: Kangaroo/puzzle71_input.txt")
    
    # Also create a smaller range for faster testing
    small_range = 2**16  # 65k keys on each side
    start_small = max(1, PREDICTED_KEY_71 - small_range)
    end_small = PREDICTED_KEY_71 + small_range
    
    with open('Kangaroo/puzzle71_small.txt', 'w') as f:
        f.write(f"{start_small:x}\n")
        f.write(f"{end_small:x}\n")
        f.write(f"{public_key}\n")
    
    print(f"Created smaller test file: Kangaroo/puzzle71_small.txt")
    print(f"Small range: 0x{start_small:x} to 0x{end_small:x} ({end_small - start_small:,} keys)")

if __name__ == "__main__":
    create_kangaroo_input() 