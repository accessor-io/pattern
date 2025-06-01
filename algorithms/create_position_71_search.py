#!/usr/bin/env python3
"""
Create Position 71 Search
========================
Search the actual 71-bit range for Position 71: 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1

# Position 71 details
TARGET_ADDRESS_71 = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
RANGE_START_71 = 0x400000000000000000  # 2^70
RANGE_END_71 = 0x7fffffffffffffffff    # 2^71 - 1

def private_key_to_address(private_key: int) -> str:
    """Convert private key to Bitcoin address (compressed)"""
    # Convert to public key
    privkey_hex = format(private_key, '064x')
    privkey_bytes = bytes.fromhex(privkey_hex)
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    
    # Compressed public key (Bitcoin puzzle uses compressed format)
    if y % 2 == 0:
        pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
    else:
        pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
    
    # Hash160 (SHA256 + RIPEMD160)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte and checksum
    versioned_payload = b'\x00' + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address_bytes = versioned_payload + checksum
    
    # Base58 encode
    address = base58.b58encode(address_bytes).decode()
    return address

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

def create_position_71_kangaroo_input():
    """Create Kangaroo input to search for Position 71"""
    
    print("Creating Position 71 Search")
    print("=" * 50)
    print(f"Target address: {TARGET_ADDRESS_71}")
    print(f"Search range: 0x{RANGE_START_71:x} to 0x{RANGE_END_71:x}")
    
    # Since we don't know the public key, we can't use Kangaroo directly
    # Instead, we need to use a different approach
    
    # Let's create a smaller search window for testing
    # Start from the beginning of the 71-bit range
    test_start = RANGE_START_71
    test_size = 2**20  # 1M keys for testing
    test_end = test_start + test_size
    
    print(f"Creating test search range: 0x{test_start:x} to 0x{test_end:x}")
    print(f"Test range size: {test_size:,} keys")
    
    # Test a few keys to verify the approach
    print("\nTesting key generation...")
    test_key = RANGE_START_71
    test_address = private_key_to_address(test_key)
    print(f"Key 0x{test_key:x} -> {test_address}")
    
    test_key = RANGE_START_71 + 1000000
    test_address = private_key_to_address(test_key)
    print(f"Key 0x{test_key:x} -> {test_address}")
    
    # Since we don't have the public key for Position 71, we need to brute force search
    # This would require a tool like BitCrack or keyhunt instead of Kangaroo
    
    print("\n" + "="*50)
    print("SOLUTION APPROACH:")
    print("Since Position 71 is unsolved and we don't have the public key,")
    print("we cannot use Kangaroo (which requires the public key).")
    print("Instead, we need to use tools like:")
    print("1. BitCrack (GPU-based address search)")
    print("2. keyhunt (CPU/GPU-based address search)")
    print("3. VanitySearch (address search)")
    print("")
    print("Command examples:")
    print(f"BitCrack: ./BitCrack -t 0 -b 71 {TARGET_ADDRESS_71}")
    print(f"keyhunt: ./keyhunt -m address -f addresses.txt -b 71 -R")
    print("")
    print("These tools search by generating private keys and checking")
    print("if they produce the target address, rather than requiring")
    print("the public key like Kangaroo does.")

if __name__ == "__main__":
    create_position_71_kangaroo_input() 